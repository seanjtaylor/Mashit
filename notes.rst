Converting mp3 to wav
=====================

install mpg123::

  sudo brew install mpg123

run the command line conversion::

  mpg123 -w <wav file> <mp3 file> 


Slicing Syntax
==============

I found it impossible to do slicing with non-integers::

  s = Snip(...)
  s[:8] # fine
  s[:8.2] # 'Snip' object is unsubscriptable

An alternative I am using until something more natural occurs to me::

  s(0,8.2) # overrides __call__
  s(8.2)   # same thing

