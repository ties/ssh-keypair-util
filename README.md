A ssh keypair utility
=================================================
`python sshkey.py genkey user@hostname.fqdn.tld --alias hostname`

I noticed that my SSH key management was not up to the best practices I
intended to follow:

  0. Use the modern format for ssh keys, which uses a modern key derivation
  	function.
  1. Use a unique key per `user@host`.
  2. Use modern key types (elliptic curves) when available.
  3. Configuring the `~/.ssh/config` file correctly

I automated the process of creating a SSH key and adding it to my config,
by using [Augeas](http://augeas.net/) to manage the configuration file, and
calling `ssh-keygen` directly from Python (...).

*This code is provided as a proof of concept. Please read it carefully before
using.*

Dependencies
-------------------------------------------------
  * `python-augeas`
  * Augeas itself (available as a package on most distributions)
