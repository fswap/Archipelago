# Elden Ring Multiworld Setup Guide

This guide covers installing the Elden Ring Archipelago randomizer, generating a game, and
connecting to a multiworld.

## Required Software

- **Elden Ring** on PC (Steam), including the **Shadow of the Erdtree** DLC if you intend to play
  DLC-enabled seeds.
- The **Elden Ring Archipelago randomizer** (generates the modified game data).
- The **Elden Ring Archipelago client** (the runtime that talks to the Archipelago server, grants
  received items, and reports your checks).
- A copy of the latest Archipelago release for generating multiworlds, if you are also the host.

> Always run the randomizer offline / with anti-cheat (EAC) disabled, exactly as you would for any
> Elden Ring mod. Use a backup of your save and a separate, modded copy of the game.

## Installing the Randomizer

1. Download and unpack the Elden Ring Archipelago randomizer following the project's README.
2. Point it at your Elden Ring installation when prompted.
3. Keep the randomizer and the client versions in sync - the slot data carries a version contract
   and the client will refuse to connect to a mismatched seed.

## Creating Your Options File

1. Generate a template options (`.yaml`) file from the
   [Options Page](/games/EldenRing/player-options), or copy an existing Elden Ring template.
2. Set at least your **Ending Condition**, **World Logic**, and whether the **DLC** is enabled.
   Other options (enemy randomization, region count, grace handling, scaling) are optional.
3. Save the file with your slot name.

## Generating a Game

- **Single-player / self-host:** run the randomizer's generate step with your `.yaml` to produce
  the modified game data and an Archipelago output.
- **Multiworld:** place your `.yaml` with the other players' files and generate the multiworld the
  same way you would for any Archipelago game, then host the resulting output.

## Joining a Multiworld Game

1. Launch Elden Ring through the Archipelago client (with EAC disabled, on your modded copy).
2. In the client, enter the server address, your slot name, and the room password if there is one.
3. Load into your save. The client grants any items you have already been sent, then keeps granting
   received items and reporting your checks as you play.

## Troubleshooting

- **The client will not connect / version mismatch:** make sure the randomizer that built the seed
  and the client are the same version.
- **Items are not arriving:** confirm the client shows a connected status and that you have loaded
  fully into the game world (not just the title screen).
- **A region will not open:** under a lock-based World Logic you need the received key item (or the
  required bosses) for that region; check your tracker or the client log for which lock is pending.
