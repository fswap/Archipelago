# Sekiro: Shadows Die Twice Randomizer Setup Guide

### Please note that this implementation is currently in alpha.

### This means things may be broken and not all options are supported yet.

## Required Software

- [Sekiro: Shadows Die Twice]
- [Sekiro: Shadows Die Twice AP Client]

[Sekiro: Shadows Die Twice]: 
https://store.steampowered.com/app/814380/Sekiro_Shadows_Die_Twice/
[Sekiro: Shadows Die Twice AP Client]:
https://github.com/fswap/from-software-archipelago-clients/releases?q=Sekiro

## Optional Software

Hopefully coming soon!

## Setting Up

First, download the client from the link above (`Sekiro Archipelago.*.zip`). It
doesn't need to go into any particular directory; it'll automatically locate 
_Sekiro_ in your Steam installation folder.

This randomizer _only_ supports the latest version of _Sekiro_, 1.06. This
is the latest version, so you don't need to do any downpatching! However, if
you've already downpatched your game to use an older version of the randomizer, 
you'll need to reinstall the latest version before using this version. You 
should also delete the `dinput8.dll` file if you still have one from an older 
randomizer version.

### One-Time Setup

Before you first connect to a multiworld, you need to generate the local data
files for your world's randomized item and (optionally) enemy locations. You 
only need to do this once per multiworld.

1. Before you first connect to a multiworld, run
   `randomizer\SekiroRandomizer.exe`.

2. Put in your Archipelago room address (usually something like
   `archipelago.gg:12345`), your player name (also known as your "slot name"), 
   and your password if you have one.

3. Click "Load" and wait a minute or two.

### Running and Connecting the Game

To run _Sekiro_ in Archipelago mode:

1. To prevent you from getting penalized, **make sure to set _Sekiro_ to offline
   mode in the game options.**

2. Run `launch-sekiro.bat`. This will start _Sekiro_ with an in-game overlay
   that you can use to interact with the Archipelago server.

3. Start playing as normal. An "Archipelago connected" message will appear
   onscreen once you have control of your character and the connection is 
   established.

## Frequently Asked Questions

### Where do I get a config file?

The [AP client archive] includes an options template. You can also use the
Options Creator in the Archipelago Launcher to configure your personal options 
and export them into a config file.

[AP client archive]: 
https://github.com/fswap/from-software-archipelago-clients/releases?q=Sekiro

### Does this work with Proton?

The *Sekiro* Archipelago randomizer supports running on Linux under Proton.
There are a few things to keep in mind:

* Because `SekiroRandomizer.exe` relies on the .NET runtime, you'll need to
  install the [.NET Runtime] under **plain [WINE]**, then run 
  `SekiroRandomizer.exe` under plain WINE as well. It won't work as a Proton 
  app!

* To run the game itself, just run `launch-sekiro.bat` under Proton.

[.NET Runtime]: https://dotnet.microsoft.com/en-us/download/dotnet/6.0
[WINE]: https://www.winehq.org/

## Troubleshooting

### Enemy randomizer issues

The Sekiro Archipelago randomizer uses [thefifthmatt's Sekiro enemy and 
item randomizer], essentially unchanged for the enemies. Unfortunately, this 
randomizer has a few known issues, including enemy AI not working, enemies 
spawning in places they can't be killed, and, in a few rare cases, enemies
spawning in ways that crash the game when they load. These bugs should be 
[reported upstream], but unfortunately the Archipelago devs can't help much 
with them.

[thefifthmatt's Sekiro enemy and item randomizer]: 
https://www.nexusmods.com/sekiro/mods/543

[reported upstream]: https://github.com/thefifthmatt/SoulsRandomizers/issues

Because in rare cases the enemy randomizer can cause seeds to be impossible to
complete, we recommend disabling it for large async multiworlds for safety
purposes.

### `launch-sekiro.bat` isn't working

Sometimes `launch-sekiro.bat` will briefly flash a terminal on your screen and 
then terminate without actually starting the game. This is usually caused by 
some issue communicating with Steam either to find `Sekiro.exe` or to launch it 
properly. If this is happening to you, make sure:

* You have Sekiro 1.06 installed. This is the latest patch as of March 2026.

* Steam is not running in administrator mode. To fix this, right-click
  `steam.exe` (by default this is in `C:\Program Files\Steam`), select
  "Properties", open the "Compatiblity" tab, and uncheck "Run this program as an
  administrator".

* There is no `dinput8.dll` file in your Sekiro game directory. This is the old
  way of installing mods, and it can interfere with the ModEngine3 workflow.

If you've checked all of these, you can also try:

* Running `launch-sekiro.bat` as an administrator.

* Reinstalling Sekiro or even reinstalling Steam itself.

* Making sure Sekiro is installed on the same drive as Steam and as the
  randomizer. (A number of users are able to run these on different drives, 
  but this has helped some users.)

If none of this works, unfortunately there's not much we can do. We use
ModEngine3 to launch Sekiro with the Archipelago mod enabled, but unfortunately
it is quite freshly released and there are still some bugs that can happen.

### `SekiroRandomizer.exe` isn't working

This is almost always caused by using a version of the randomizer client that's
not compatible with the version used to generate the multiworld. If you're
generating your multiworld on archipelago.gg, you *must* use the latest [Sekiro 
AP Client]. If you want to use a different client version, you *must* generate 
the multiworld locally using the apworld bundled with the client.

[Sekiro AP Client]: 
https://github.com/fswap/from-software-archipelago-clients/releases?q=Sekiro
