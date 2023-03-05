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


