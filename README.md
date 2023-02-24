![CrowdStrike cs.ratelimit](https://raw.githubusercontent.com/CrowdStrike/cs.ratelimit/main/docs/img/cs-logo.png)

# cs.ratelimit

This provides a threadsafe configurable rate limiter to a Python callable.

It's easy to create a rate limited function
```python
>>> from datetime import datetime, timedelta
>>> from cs import ratelimit
>>> @ratelimit.ratelimited(max_count=1, interval=timedelta(seconds=1), block=False)
... def my_func():
...     pass
>>> my_func()
>>> try:
...     my_func()
... except ratelimit.RateLimitExceeded:
...     print(u"Too fast!")
Too fast!
```
We can just as easily make it a blocking rate limiter
```python
>>> @ratelimit.ratelimited(max_count=1, interval=timedelta(seconds=1), block=True)
... def my_func():
...     pass
>>> my_func()
>>> my_func() # blocks, doesn't raise

```

It's also easy to create a class-level rate limited method
```python
>>> class MyClass1:
...     @ratelimit.ratelimitedmethod(max_count=1, interval=timedelta(seconds=1), block=False)
...     def my_method(self):
...         pass
>>> instance1 = MyClass1()
>>> instance2 = MyClass1()
>>> instance1.my_method()
>>> try:
...     instance2.my_method()
... except ratelimit.RateLimitExceeded:
...     print(u"Too fast!")
Too fast!
```

A more advanced use case is per-instance limiters
```python
>>> from operator import attrgetter
>>> class MyClass2:
...     def __init__(self):
...         self.rl = ratelimit.RateLimitProperties(max_count=1,
...                                       interval=timedelta(seconds=1),
...                                       block=False)
...     @ratelimit.ratelimitedmethod(attrgetter('rl'))
...     def my_method(self):
...         pass
>>> instance1 = MyClass2()
>>> instance2 = MyClass2()

The rate limiters in these instances are independent
>>> instance1.my_method()
>>> instance2.my_method()
>>> try:
...     instance1.my_method()
... except ratelimit.RateLimitExceeded:
...     print(u"Too fast!")
Too fast!
```
They can also be updated at any time
```python
>>> with instance2.rl.rlock: #needed in threaded environments
...     instance2.rl.max_count = 2
>>> instance2.my_method()

```


---

<p align="center">
  <img src="https://raw.githubusercontent.com/CrowdStrike/cs.ratelimit/main/docs/img/cs-logo-footer.png"><br/>
  <img width="300px" src="https://raw.githubusercontent.com/CrowdStrike/cs.ratelimit/main/docs/img/alliance_team.png">
</p>
<h3><p align="center">WE STOP BREACHES</p></h3>