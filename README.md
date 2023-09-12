<p align="center">
  <img src="docs/cutie.png">
</p>

CuteRAT is a Remote Access Trojan (RAT) that only uses [bash builtins](https://www.gnu.org/software/bash/manual/html_node/Bash-Builtins.html) to provide an encrypted reverse shell for quick triaging of a new machine.

*Disclaimer: This is a tool meant for red teaming and penetration testing and the author does not condone it being used in other ways*

## Why?
Sometimes you don't want to run more binaries than you have to on an engagement. Maybe your target's EDR is picking up on the executions of common tools, or maybe you're hacking in the 1990's and there's [`pacct`](https://www.linuxjournal.com/article/6144) enabled on your box. In those cases you'll want some basic remote functionality without having to rely on external processes - enter CuteRAT! 

CuteRAT leverages the fact that its difficult to examine what is happening in a shell process short of attaching a debugger to it. Combine the delivery of CuteRAT with a non-interactive shell and you've got a pretty stealthy shell on your hands!

Developing CuteRAT has been a good exercise in understanding the full functionalities of the `bash` shell. Given `bash` is a [turing complete language](https://en.wikibooks.org/wiki/Bash_Shell_Scripting/A_Few_Notes_On_Terminology), you could theoretically implement **any** complex routine as a built in - as long as you're willing to accept slowed execution.

## Features
- Deployed via a pastable from an SSH session and `nohup`'ed so you can exit the shell. Alternatively you can run it directly from a non-interactive shell - this exercise is left up to the user.
- All the functionality is managed by the server-side with client-side only handling comms. Comes with built in payload support and pre-made payloads that emulate common UNIX functionality.
- Works on any system with a recent install of Bash (`>=2.04` with `--enable-net-redirections` option).
- Encrypted callback comms using xor with a pre-defined key.
- Slow on large output!

## Deploying

To build a new CuteRAT, run `cuterat.py` in `build` mode and provide the callback and key params:

```bash
$ python3 cuterat.py build --bind 127.0.0.1:31337 --key deadbeef
```

This will generate a pastable CuteRAT that can be run from any shell on the target system. Start a listener on your C2 to get ready to catch the callback. Note that the arguments are the same (assuming no redirection infrastructure) and only the mode changed to `listen`:

```bash
$ python cuterat.py listen --bind 127.0.0.1:31337 --key deadbeef
```

Now paste the output of the `build` command in a shell on your target and you should receive a callback from CuteRAT. Seeing as the RAT was started with `nohup`, you can exit your ssh session and rely on the comms to provide your access.

## Payloads

In keeping with the theme of bash builtins, CuteRAT comes with a set of payloads that can be invoked when actively connected to a deployment. These payloads seek to immitate common UNIX utilities using only bash builtin commands and in the most portable manner possible.

- From an active CuteRAT shell, you can list available payloads with `~help`
- To get help on a specific payload, type `~help <payload_name>`

Custom payloads can be added to CuteRAT and dropped to the `payloads` directory. They don't have to be comprised of only bash builtins - as long as they can be executed as a single string if passed to a shell (ie, use `;` to delimit commands) it should work fine! Hell, you could even get CuteRAT to deploy heavier red teaming tools such as [Mythic](https://github.com/its-a-feature/Mythic).

## Improvements

Eventually I'd like to get to the following improvements:

- Execution via non-interactive shell to bypass known [command logging tricks like `PROMPT_COMMAND`](https://tpaschalis.me/command-prompt-logging/). There are other ways around this if you have exeprience with UNIX logging.
- Run CuteRAT execution up against a tricked out box with `auditd`. I have a suspicion that even though `auditd` could hook `execve` syscalls, you could hide the commands being run from CuteRAT tasks by leveraging `bash` reading from `STDIN`.
- Better xor'ing. My xor and string manipulation functions have room for improvement. I suspect I could make the whole process more efficient for large output by getting the key size closer to `MAX_INT`.


*Trivia: It's called CuteRAT because it's small (only 850 bytes!) and is trying its best.*
