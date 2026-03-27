# XY-STAGE - A quick and dirty framework for EMFI Fault Injection 

## Overview
This is a basic console-based application xy_stage.py (and supporting files) to control 3D-Printer to perform XY scans on various selectable CPU architectures I am working with. It is really rough python code but at least it useable (for me). Use it and your own risk and swear at it privately. 

Notes:  I am a C++ Programmer. I rather dislike (IMO) the way abstract types in Python but I wanted common abstract class defined interface so I use python's kludgy ways. Seriously, I might rewrite all of this in Modern C++. 

## Credit
Much of this is based on source code written by Colin O'Flynn or NewAE Technology. Hence, any code I write for my own use also includes Colin O'Flynn/NewAE license headers. 

## Basic Functionality
- Uses Python OOP inheritance (or lack of) in the form of abstract class to define common methods needed to XY scan a chip and attack a chip with an EMFI pulse.
- There is an abstract class for xy scanners (allowing one for 3D printers and one for CNC Machines)
- Supports Serial Wire Debug
- Supports Power-off, Power-On board reset support after a USB corrupting EMFI pulse

## It currently supports the following Targets:
- as6c3216A SRAM
- STM32H7
- STM32L5 (not checked in yet)

  
