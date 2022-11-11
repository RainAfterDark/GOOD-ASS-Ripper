# GOOD-ASS-Ripper
Player data ripper to GOOD format for certain anime game with Akebi-Sniffer-Scripting (ASS)

## Usage
- Setting up Akebi and Sniffer
  - `git clone https://github.com/RainAfterDark/GOOD-ASS-Ripper.git`
  - Get the latest release of [Akebi](https://github.com/Akebi-Group/Akebi-GC).
  - Build my fork of [Akebi-Sniffer](https://github.com/RainAfterDark/Akebi-PacketSniffer) or download my [unofficial release](https://github.com/RainAfterDark/Akebi-PacketSniffer/releases). (until my [PR](https://github.com/Akebi-Group/Akebi-PacketSniffer/pull/10) gets merged)
  - After injecting the game with Akebi, open the menu, go to settings, and all the way down, turn on "Capturing".
  - Open up the sniffer, set-up your protos (you can get [Sorapointa's](https://github.com/Sorapointa/Sorapointa-Protos)) and load the script `ripper.lua` from wherever you may have placed it. A simple video tutorial for setting up the sniffer should be in the repo's README.

- Using the script
  - Modify the item filters in `ripper.lua` to your needs.
  - Load the script in the main filter before logging in to the game (just right before the door opens). Press "Apply".
  - Log in to the game as usual.
  - Check console logs, if you've gotten an "Export success!" then you can head over to your PacketSniffer directory and see your exported data as `GOOD-ASS-Rip.json`.
  - You can still modify your item filters in the source code after this, just press "Apply" again after saving changes to regenerate your data.

This script both supports importing character and equipment data to [GO](https://frzyc.github.io/genshin-optimizer/#/) and material data to [SEELIE.me](https://seelie.me)
