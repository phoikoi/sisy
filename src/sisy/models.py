import inspect
import json
import pytz
from datetime import datetime
from importlib import import_module

from django.db import models
from django.conf import settings
from django.utils import timezone

from channels import Channel
from croniter import croniter

from sisy import RUN_TASK_CHANNEL, KILL_TASK_CHANNEL, DEFAULT_SCHEDULE

TZ = pytz.timezone(settings.TIME_ZONE)

HAS_NOT_RUN = datetime(1970, 1, 1, 0, 0, tzinfo=timezone.utc)
FAR_FUTURE = datetime(2217, 12, 31, 23, 59, tzinfo=timezone.utc)

fullpath = lambda x:f"{x.__module__}.{x.__qualname__}"

def get_member(thing_obj, member_string):
    """Get a member from an object by (string) name"""
    mems = {x[0]: x[1] for x in inspect.getmembers(thing_obj)}
    if member_string in mems:
        return mems[member_string]

def get_module_member_by_dottedpath(dottedpath):
    components = dottedpath.split('.')
    module_name = '.'.join(components[:-1])
    thing_name = components[-1]
    mod = import_module(module_name)
    return get_member(mod, thing_name)

def get_func_info(thing):
    if inspect.isfunction(thing):
        sig = [x for x in inspect.signature(thing).parameters]
        if sig[0] == 'self':
            raise ValueError("Cannot call unbound instance method")
        if thing.__name__ == thing.__qualname__:
            functype = 'function'
            info = dict(
                func_type=functype,
                module_name=thing.__module__,
                func_name=thing.__name__,
                func_path=fullpath(thing),
            )
        else:
            functype = 'staticmethod'
            classname = thing.__qualname__.split('.')[0]
            class_dottedpath = f"{thing.__module__}.{classname}"

            info = dict(
                func_type=functype,
                module_name=thing.__module__,
                class_name=classname,
                class_path=class_dottedpath,
                func_name=thing.__name__,
                func_path=fullpath(thing),
            )

        return info

    elif inspect.ismethod(thing):
        if inspect.isclass(thing.__self__):
            return dict(
                func_type='classmethod',
                module_name=thing.__self__.__module__,
                class_name=thing.__self__.__name__,
                class_path=fullpath(thing.__self__),
                func_name=thing.__name__,
                func_path=fullpath(thing),
            )

        mro = [fullpath(x) for x in inspect.getmro(thing.__self__.__class__)]
        # bases = [fullpath(x) for x in thing.__self__.__class__.__bases__]
        if 'django.db.models.base.Model' not in mro:
            raise ValueError(f"Can only call instance methods of Django model objects, not {fullpath(thing)}.")

        model_obj = thing.__self__
        model_pk = model_obj.pk
        return dict(
            func_type='instancemethod',
            module_name=model_obj.__class__.__module__,
            class_name=model_obj.__class__.__name__,
            class_path=fullpath(model_obj.__class__),
            model_pk=model_pk,
            func_name=thing.__name__,
            func_path=fullpath(thing),
        )
    else:
        raise ValueError(f"{fullpath(thing)} is not a callable object")

def func_from_string(callable_str):
    """Return a live function from a full dotted path.  Must be either a plain function
    directly in a module, a class function, or a static function.  (No modules, classes,
    or instance methods, since those can't be called as tasks.)"""
    components = callable_str.split('.')

    func = None

    if len(components) < 2:
        raise ValueError("Need full dotted path to task function")
    elif len(components) == 2:
        mod_name = components[0]
        func_name = components[1]
        try:
            mod = import_module(mod_name)
        except ModuleNotFoundError:
            raise ValueError(f"Module {mod_name} not found")
        func = get_member(mod, func_name)
        if func is None:
            raise ValueError(f"{func_name} is not a member of {mod_name}")
    else:
        mod_name = '.'.join(components[:-1])
        func_name = components[-1]

        try:
            mod = import_module(mod_name)
        except ModuleNotFoundError:
            mod_name = '.'.join(components[:-2])
            class_name = components[-2]

            try:
                mod = import_module(mod_name)
            except ModuleNotFoundError:
                raise ValueError(f"Module {mod_name} not found")

            klass = get_member(mod, class_name)
            if klass is None:
                raise ValueError(f"Class {class_name} is not a member of {mod_name}")

            func = get_member(klass, func_name)
            if func is None:
                raise ValueError(f"Function {func_name} is not a member of {mod_name}.{class_name}")

        if func is None:
            func = get_member(mod, func_name)
            if func is None:
                raise ValueError(f"Function {func_name} is not a member of {mod_name}")

    if inspect.ismodule(func):
        raise ValueError("Cannot call module directly")

    if inspect.isclass(func):
        raise ValueError("Cannot call class directly")

    try:
        sig = [x for x in inspect.signature(func).parameters]
    except TypeError:
        raise ValueError(f"{callable_str} ({str(type(func))[1:-1]}) is not a callable object")

    if len(sig) == 1:
        if sig[0] == 'message':
            return func
        else:
            raise ValueError("Task function must have one parameter, named 'message'")

    elif len(sig)==2 and sig[0]=='self' and sig[1]=='message':
        # We only check for the conventional 'self', but if you're using something else,
        # you deserve the pain you'll have trying to debug this.
        raise ValueError("Can't call instance method without an instance! (Try sisy.models.task_with_callable)")
    else:
        raise ValueError("Improper signature for task function (needs only 'message')")

def funcinfo_from_string(callable_str):
    return get_func_info(func_from_string(callable_str))

class Task(models.Model):
    """Main object model, keeps task state between workers"""
    created_at = models.DateTimeField(auto_now_add=True, help_text="(automatic)")
    modified_at = models.DateTimeField(auto_now = True, help_text="(automatic)")
    label = models.CharField(max_length=255, help_text="(required) Name of task, normally the same as the callback string")
    schedule = models.CharField(max_length=80, default=DEFAULT_SCHEDULE, help_text="(required) Cron-format schedule for running the task")
    last_run = models.DateTimeField(default=HAS_NOT_RUN, blank=True, null=True, help_text="(automatic)")
    next_run = models.DateTimeField(default=HAS_NOT_RUN, blank=True, null=True, help_text="(automatic)")
    enabled = models.BooleanField(default=True, help_text="(optional) If false, sisy will skip this task")
    _func_info = models.TextField(default='{}', blank=True, help_text="(internal) Dictionary of callable function info, stored as JSON")
    _extra_data = models.TextField(default='{}', blank=True, help_text="(internal) Dictionary of user data, stored as JSON.   Normally accessed only through the ``userdata`` property.")
    wait_for_schedule = models.BooleanField(default=True, help_text="(optional) Should the task wait for its first cron schedule, or run immediately")
    iterations = models.IntegerField(default=0, help_text="(optional) Run the task this many times, then kill it")
    allow_overlap = models.BooleanField(default=True, help_text="(optional) Should sisy allow more than one instance of this task to run at once")
    running = models.BooleanField(default=False, help_text="(automatic) Is a worker actually running the task at the moment")
    start_running = models.DateTimeField(default=HAS_NOT_RUN, help_text="(optional) Date and time when task will start running")
    end_running = models.DateTimeField(default=FAR_FUTURE, help_text="(optional) Date and time when task will stop running")

    def __str__(self):
        return f"Task {self.pk}"

    @property
    def userdata(self):
        return json.loads(self._extra_data)


    @userdata.setter
    def userdata(self, data):
        self._extra_data = json.dumps(data)

    @property
    def funcinfo(self):
        return json.loads(self._func_info)

    @funcinfo.setter
    def funcinfo(self, data):
        self._func_info = json.dumps(data)

    def func_from_info(self):
        """Find and return a callable object from a task info dictionary"""
        info = self.funcinfo
        functype = info['func_type']
        if functype in ['instancemethod', 'classmethod', 'staticmethod']:
            the_modelclass = get_module_member_by_dottedpath(info['class_path'])
            if functype == 'instancemethod':
                the_modelobject = the_modelclass.objects.get(pk=info['model_pk'])
                the_callable = get_member(the_modelobject, info['func_name'])
            else:
                the_callable = get_member(the_modelclass, info['func_name'])
            return the_callable
        elif functype == 'function':
            mod = import_module(info['module_name'])
            the_callable = get_member(mod, info['func_name'])
            return the_callable
        else:
            raise ValueError(f"Unknown functype '{functype} in task {self.pk} ({self.label})")

    @classmethod
    def run_tasks(cls):
        """Internal task-runner class method, called by :py:func:`sisy.consumers.run_heartbeat`"""
        now = timezone.now()
        tasks = cls.objects.filter(enabled=True)
        for task in tasks:
            if task.next_run == HAS_NOT_RUN:
                task.calc_next_run()
            if task.next_run < now:
                if (task.start_running < now):
                    if (task.end_running > now):
                        task.run_asap()
                    else:
                        task.enabled = False
                        task.save()
                        Channel(KILL_TASK_CHANNEL).send({'id': task.pk})

    def calc_next_run(self):
        """Calculate next run time of this task"""
        base_time = self.last_run
        if self.last_run == HAS_NOT_RUN:
            if self.wait_for_schedule is False:
                self.next_run = timezone.now()
                self.wait_for_schedule = False # reset so we don't run on every clock tick
                self.save()
                return
            else:
                base_time = timezone.now()
        self.next_run = croniter(self.schedule, base_time).get_next(datetime)
        self.save()

    def submit(self, timestamp):
        """Internal instance method to submit this task for running immediately.
        Does not handle any iteration, end-date, etc., processing."""
        Channel(RUN_TASK_CHANNEL).send({'id':self.pk, 'ts': timestamp.timestamp()})

    def run(self, message):
        """Internal instance method run by worker process to actually run the task callable."""
        the_callable = self.func_from_info()
        try:
            task_message = dict(
                task=self,
                channel_message=message,
            )
            the_callable(task_message)
        finally:
            if self.end_running < self.next_run:
                self.enabled=False
                Channel(KILL_TASK_CHANNEL).send({'id': self.pk})
                return
            if self.iterations == 0:
                return
            else:
                self.iterations -= 1
                if self.iterations == 0:
                    self.enabled = False
                    Channel(KILL_TASK_CHANNEL).send({'id':self.pk})
                self.save()

    def run_asap(self):
        """Instance method to run this task immediately."""
        now = timezone.now()
        self.last_run = now
        self.calc_next_run()
        self.save()
        self.submit(now)

    @classmethod
    def run_iterations(cls, the_callable, iterations=1, label=None, schedule='* * * * * *', userdata = None, run_immediately=False, delay_until=None):
        """Class method to run a callable with a specified number of iterations"""
        task = task_with_callable(the_callable, label=label, schedule=schedule, userdata=userdata)
        task.iterations = iterations
        if delay_until is not None:
            if isinstance(delay_until, datetime):
                if delay_until > timezone.now():
                    task.start_running = delay_until
                else:
                    raise ValueError("Task cannot start running in the past")
            else:
                raise ValueError("delay_until must be a datetime.datetime instance")
        if run_immediately:
            task.next_run = timezone.now()
        else:
            task.calc_next_run()
        task.save()

    @classmethod
    def run_once(cls, the_callable, userdata=None, delay_until=None):
        """Class method to run a one-shot task, immediately."""
        cls.run_iterations(the_callable, userdata=userdata, run_immediately=True, delay_until=delay_until)


def task_with_callable(the_callable, label=None, schedule=DEFAULT_SCHEDULE, userdata=None, pk_override=None):
    """Factory function to create a properly initialized task."""
    task = Task()
    if isinstance(the_callable, str):
        if pk_override is not None:
            components = the_callable.split('.')
            info = dict(
                func_type='instancemethod',
                module_name='.'.join(components[:-2]),
                class_name=components[-2],
                class_path='.'.join(components[:-1]),
                model_pk=pk_override,
                func_name=components[-1],
                func_path=the_callable,
            )
            task.funcinfo = info
        else:
            task.funcinfo = get_func_info(func_from_string(the_callable))
    else:
        task.funcinfo = get_func_info(the_callable)

    if label is None:
        task.label = task.funcinfo['func_path']
    else:
        task.label = label

    task.schedule = schedule
    if not croniter.is_valid(task.schedule):
        raise ValueError(f"Cron schedule {task.schedule} is not valid")
    
    if userdata is None:
        task.userdata = dict()
    else:
        if isinstance(userdata, dict):
            task.userdata = userdata
        else:
            raise ValueError("Userdata must be a dictionary of JSON-serializable data")

    return task

def taskinfo_with_label(label):
    """Return task info dictionary from task label.  Internal function,
    pretty much only used in migrations since the model methods aren't there."""
    task = Task.objects.get(label=label)
    info = json.loads(task._func_info)
    return info
