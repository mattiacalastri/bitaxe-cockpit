# VHS tape — live cockpit recording for README hero
# Captures the traveling-wave BITAXE animation + live panels on a real Gamma 601.
# Render with: vhs docs/cockpit-onda-hero.tape
#
# Requires: vhs (brew install vhs), a reachable Bitaxe at $BITAXE_HOST,
# and `pip install -e .` so the `bitaxe-cockpit` binary is on PATH.

Output docs/cockpit-onda-hero.gif

Set Shell "zsh"
Set FontSize 14
Set Width 1600
Set Height 1100
Set Framerate 24
Set PlaybackSpeed 1.0
Set Theme "Dracula"
Set TypingSpeed 40ms
Set LoopOffset 5%

# Set env so the cockpit talks to the real Gamma 601 on the LAN.
# Use absolute paths because VHS spawns a clean shell without our PATH.
Hide
Type "export BITAXE_HOST=192.168.1.64" Enter
Type "export PATH=/opt/homebrew/bin:/usr/local/bin:$PATH" Enter
Sleep 200ms
Type "clear" Enter
Sleep 300ms
Show

# Launch the cockpit. The first 2 seconds show the ASCII title settling
# in, then the traveling wave kicks in and the live panels populate.
Type "/opt/homebrew/bin/bitaxe-cockpit"
Sleep 500ms
Enter

# Let the wave travel + panels animate for a full cycle.
Sleep 14s

# Quit cleanly so the recording ends without a stack trace.
Type "q"
Sleep 800ms
