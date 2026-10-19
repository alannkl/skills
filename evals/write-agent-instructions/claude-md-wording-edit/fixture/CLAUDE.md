# Project instructions

It is really important that you, as the agent working in this repository, always make sure to follow these instructions at all times when you are doing any work here.

- In terms of git, please do not ever push directly to the main branch under any circumstances; what you should do instead is open a pull request so that a human is able to review it.
- When it comes to commit messages, these should be written in the Conventional Commits format (for example `feat:` or `fix:`), and the reason for this is that the release bot parses the prefixes in order to build the changelog.
- If and when you happen to be making changes that touch the billing module (which lives in `src/billing/`), you should go and read `docs/billing-rules.md` first before you make any of those changes.
- Tests can be run by using the command `make test`, and you should run them before you go ahead and open a pull request.
- Format your replies to the user in Markdown.
