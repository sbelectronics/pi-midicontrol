#Raspberry Pi Midi Player Frontend
Scott Baker, http://www.smbaker.com/

## Introduction

This project is a raspberry pip midi player. It uses two custom hats -- smbaker's Midi Hat and smbaker's VFD hat. The first one provides midi in, out, and through jacks that are connected to the rasbperry pi's uart. The second one implements a simple control interface using a VFD (or LCD), encoder, and some buttons.

## Required software

Install the following:

- ttymidi custom fork to support 31250 baud: https://github.com/sbelectronics/ttymidi
- aplaymidi

## Usage

`console_player.py` is a console client used for testing, using keyboard and screen instead of the VFD.

`vfd_player.py` is a client that uses the VFD display, encoder, and buttons.

Specify the directory on the command line with the `-d` option, for example: `python vfd_player.py -d /midi`. If no `-d` option is specified, then the program will attempt to find midi files in the `files/` subdirectory of the current working directory.

## Interface

Press the encoder down to switch the cursor between folder and file selection mode. Rotate the encoder to move to a new file (or a new folder).

The rightmost button can be used to engage "fast mode". In fast mode, if the cursor is set to song, then each tick of the encoder moves ten songs instead of one. 

If using fast mode on while the cursor is set folders, then it will attempt to skip sub-folders (for example, if there is `/a/foo`, `/a/bar`, and `/b/foo` then fast mode would skip from `/a/foo` to `/b/foo`).   
