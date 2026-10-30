= User facing changes between releases

Unreleased:

v1.4.9

- Bug fix: archive --with-notes would clobber the main user. This
  resulted in the wrong user being shown in the header of an HTML
  export.
- Bug fix: save backup file when no backup file exists.
- Feature: Use shorter media directory names, if possible. Depending
  on file system and fedi server used, users could run into "file name
  too long" errors.
- Feature: --no-version-check is now the default.
- Feature: allow suppression of media download errors.
- Feature: add followed-tags and filters commands.
- Feature: better handling of rate-limiting and media download pacing.
- Bug fix: fixed a typo that resulted in a runtime error (`data_handler`
  instead of `date_handler`).

Thanks Jonathan Kamens, Feiko Nanninga, Tim McCormack.

v1.4.8

- Add new archive --update option to update existing items. Thanks,
  Jonathan Kamens.
- Don't keep trying to download files with permanent download errors.
  Thanks, Jonathan Kamens.

v1.4.7 was a bug fix release.

v1.4.6

- Rename whitelist to allowlist.
- Save the archive while expiring toots since this tends to run very
  long.

v1.4.5

- Better HTML export. Thanks, legogo29.
- Delay and retry upon 429 responses when downloading media. thanks,
  Stefan Schlott.

v1.4.4

- Prevent exceptions when many statuses are empty. Thanks, Florian
  Cargoët.
- Show videos in the HTML export.
  Thanks, Amos Blanton.
- Allow media images to be shown instead of squished down to 110 px.
  Thanks, Amos Blanton.
- Add --with-mutes, --with-blocks, --with-notes to archive command.
  Add global --quiet option and media --suppress-errors option.
  Thanks, Jonathan Kamens.
- Fix bookmarks support.
- Lazy image loading.

v1.4.3

- Add mastosearch, mastoarch and upgrade_python-mastodon.sh to contrib
  folder. Thanks, Izzy.

...

Patches contributing past entries to this list happily accepted.

