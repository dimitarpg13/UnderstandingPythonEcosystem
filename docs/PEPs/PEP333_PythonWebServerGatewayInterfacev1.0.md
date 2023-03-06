# PEP 333 - Python Web Server Gateway Interface v1.0

## Preface
Note: for an updated version of this spec that supports Python 3.x and includes community errata, addenda, and clarifications, please see PEP 3333 instead.

## Abstarct

This document specifies a proposed standard interface between web servers and Python web applications or frameworks to promote web application portability across a variety of web servers.

## Rationale and Goals

Python currently boasts a wide variety of web application frameworks. This wide variety of choices can be a problem for new Python users, because generally speaking, their choice of web framework will limit their choice of usable web servers, and vice versa.

By contrast, although Java has just as many web application frameworks available, Java's servlet API makes it possible for applications written with any Java web application framework to run in any web server that supports the servlet API.

The availability and widespread use of such an API in web servers for Python - whether those servers are written in Python (e.g. Medusa), embed Python (e.g. mod_python), or invoke Python via a gateway protocol (e.g. CGI, FastCGI,etc.) - would separate choice of framework from choice of web server, freeing users to choose a pairing that suits them, while freeing framework and server developers to focus on their preferred area of specialization.

This PEP, therefore, proporses a simple and universal interface between web servers and web applications or frameworks: the Python Web Server Gateway Interface (WSGI).

But the mere existence of a WSGI spec foes nothing to address the existing state of servers and frameworks for Python web applications. Server and framework authors must actually implement WSGI for there to be any effect. 

WSGI __must__ be easy to implement, so that an author's initial investment in the interface can be reasonably low.

Thus, simplicity of implementation on _both_ the server and framework sides of the interface is absolutely critical to the utility of the WSGI interface, and is therefore the prinicpal criterion for any design decisions.

Note, howeverm that simplicity of implementation for a framework author is not the same thing as ease of use for a web application author. WSGI presents an absolutely "no frills" interface to the framework author, because bells and whistles like response objects and cookie handling would just get in the way of existing frameworks' handling of these issues. Again, the goal of WSGI is to facilitate easy interconnection of existing servers and applications or frameworks, not to create a new
web framework.

Note also that this goal precludes WSGI from requiring anything that is not already available in deployed versions of Python. Therefore, new standard library modules are not proposed or required by this specification, and nothing in WSGI requires a Python version greater than 2.2.2.

In addition to ease of implementaton for existing and future frameworks and servers, it should also be easy to create request preprocessors, response post processors, and other WSGI-based "middleware" components that look like an application to their containing server, while acting as a server for their contained applications.

If middleware can be both simple and robust, and WSGI is widely available in servers and frameworks, it allows for the possibility of an entirely new kind of Python web application framework: one consisting of loosely-coupled WSGI middleware components. Indeed, existing framework authors may even choose to refactor their frameworks' existing services to be provided in this way, becoming more like librarires used with WSGI, and less like monolithic frameworks. This would then allow
application developers to choose "best-of-breed" components for specific functionality, rather than having to commit to all the pros and cons of a single framework.

Of course, as of this writing, that day is doubtless quite far off. In the meantime, it is a sufficient short term goal for WSGI to enable the use of any framework with any server.

Finally, it should be mentioned that the current version of WSGI does not prescribe any particular mechanism for "deploying" an application for use with a web server gateway.
At the present time, this is necessarily implementation-defined by the server or gateway. 

## Specification Overview

The WSGI interface has two sides: the "server" or "gateway" side, and the "application" or "framework" side. The server side invokes a callable object that is provided by the application side. The specifics of how that object is provided are up to the server or gateway. It is assumed that some servers or gateways will require an application's deployer to write a short script to create an instance of the server or gateway, and supply it with the application object. Other servers and gateways may use configuration files or other mechanisms to specify where an application object should be imported from, or otherwise obtained.

In addition to "pure" servers/gateways and applications/frameworks, it is also possible to create "middleware" components that implement both sides of this specification. Such components act as an application to their containing server, and as a server to a contained application, and can be used to provide extended APIs, content transformation, navigation, and other useful functions.

Throughout this specification, we will use the term "a callable" to mean "a function, method, class, or an instance with a `__call__` method". It is up to the server, gateway, or application implementing the callable to choose the appropriate implementation technique for their needs. Conversely, a server, gateway, or application that is invoking a callable __must not__ have any dependency on what kind of callable was provided to it. Callables are only to be called, not introspected upon.

### The Application/Framework Side

The application object is simply callable object that accepts two arguments. The term "object" should not be misconstrued as requiring an actual object instance: a function, method, class, or isntance with a `__call__` method are all acceptable for use as an application object. Application objects must be able to be invoked more than once, as virtually all servers/gateways (other than CGI) will make such repeated requests.

(Note: although we refer to it as an "application" object, this should not be construed to mean that application developers will use WSGI as a web programming API! It is assumed that application developers will continue to use existing, high-level framework services to develop their applications. WSGI is a tool for framework and server developers, and is not intended to directly support application developers.)

Here are two example application objects; one is a function, and the other is a class:

```python
def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello world!\n']

class AppClass:
    """produce the same output, but using a class
    
    (Note: 'AppClass' is the 'Application' here, so calling it 
    returns an instance of 'AppClass', which is then the iterable
    return value of the "application callable" as required by
    the spec.

    If we wanted to use *instances* of 'AppClass' as application 
    objects instead, we would have to implement a '__call__' 
    method, which would be invoked to execute the application,
    and we would need to create an instance for use by the
    server or gateway.)
    """
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

    def __iter__(self):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        self.start(status, response_headers)
        yield "Hello world!\n"
```

### The Server/Gateway Side

The server or gateway invokes the application callable once for each request it receives from an HTTP client, that is directed at the application. To illustrate, here is a simple CGI gateway, implemented as a function taking an application object. Note that this simple example has limited error handling, because by default an uncaught exception will be dumped to `sys.stderr` and logged by the web server.

```python
import os, sys

def run_with_cgi(application):

    environ = dict(os.environ.items())
    environ['wsgi.input'] = sys.stdin
    environ['wsgi.errors'] = sys.stderr
    environ['wsgi.version'] = (1, 0)
    environ['wsgi.multithread'] = False
    environ['wsgi.multiprocess'] = True
    environ['wsgi.run_once'] = True

    if environ.get('HTTPS', 'off') in ('on', '1'):
        environ['wsgi.url_scheme'] = 'https'
    else:
        environ['wsgi.url_scheme'] = 'http'

    headers_set = []
    headers_sent = []

def write(data):
    if not headers_set:
        raise AssertionError("write() before start_response()")

    elif not headers_sent:
        # Before the first output, send the stored headers
        status, response_headers = headers_sent[:] = headers_set

```

