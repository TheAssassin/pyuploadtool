# pyuploadtool

A build-system-agnostic tool for creating releases and uploading artifacts on various hosting providers.

*Inspired by [uploadtool](https://github.com/probonopd/uploadtool), but much better in so many ways...*


## Projects using pyuploadtool

- [appimagecraft](https://github.com/TheAssassin/appimagecraft/)
- [linuxdeploy](https://github.com/linuxdeploy/linuxdeploy)
- [linuxdeploy-plugin-appimage](https://github.com/linuxdeploy/linuxdeploy-plugin-appimage)
- [linuxdeploy-plugin-qt](https://github.com/linuxdeploy/linuxdeploy-plugin-qt)
- [Blue Nebula](https://blue-nebula.org/)
- [Pext](https://github.com/Pext/Pext)
- [zsync2](https://github.com/AppImage/zsync2/)
- [AppImageKit](https://github.com/AppImage/AppImageKit/)
- [AppImageUpdate](https://github.com/AppImage/AppImageUpdate/)
- [SpinED](https://github.com/twesterhout/spin-ed)

... and a lot more! Some projects can be found [on GitHub](https://github.com/search?q=pyuploadtool&type=code).


## Usage

Using this tool is fairly straightforward. Ideally, in one of the supported build environments, all you have to do is to run it! The tool figures out its configuration from the environment variables (which either are provided by the build system, or set by the user).

Please see the following sections for more information on how to use the tool with the supported build systems and release hosting providers.


## Supported build systems

This tool supports various build systems. Build system implementations are used to read metadata about a release from the environment, e.g., by processing available environment variables.

### GitHub actions

To use the tool with [GitHub actions](https://docs.github.com/en/free-pro-team@latest/github/administering-a-repository/about-releases), all you have to do is to provide `GITHUB_TOKEN` in the environment of your upload step.

The tool can easily upload files to *GitHub releases* if you make the `GITHUB_TOKEN` secret available as environment variable.

An example pipeline step look like this:

```yaml
      - name: Create release and upload artifacts
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
            wget -q https://github.com/TheAssassin/pyuploadtool/releases/download/continuous/pyuploadtool-x86_64.AppImage
            chmod +x pyuploadtool-x86_64.AppImage
            ./pyuploadtool-x86_64.AppImage myfile myotherfile
```

If you want to upload to WebDAV, too, you could use the following step:

An example pipeline step look like this:

```yaml
      - name: Create release and upload artifacts
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          WEBDAV_URL: ${{ secrets.WEBDAV_URL }}
          WEBDAV_USER: ${{ secrets.WEBDAV_USER }}
          WEBDAV_PASSWORD: ${{ secrets.WEBDAV_PASSWORD }}
        run: |
            wget -q https://github.com/TheAssassin/pyuploadtool/releases/download/continuous/pyuploadtool-x86_64.AppImage
            chmod +x pyuploadtool-x86_64.AppImage
            ./pyuploadtool-x86_64.AppImage myfile myotherfile
```


## Supported releases hosting providers

### GitHub releases

Uploading data on GitHub releases is currently supported out of the box with *GitHub actions*.

By default, the release is marked as Stable for tags, and Prerelease for continuous builds, which are released with the tag name `continuous`. It is possible to override
the tag name and release type, with the following environment variables:

- `GITHUB_CONTINUOUS_RELEASE_TYPE`: type of release to be published. (supported values: `stable`, `prerelease`, default: `stable` for tags, `prerelease` otherwise)
- `GITHUB_CONTINUOUS_RELEASE_NAME`: The title of the release (default: "Continuous Build")
- `GITHUB_CONTINUOUS_RELEASE_TAG`: The tag used for release (default: `continuous`)


### WebDAV

You can upload to any WebDAV server which supports `PUT` operations. The following environment variables need to be set:

- `$WEBDAV_URL`: URL to the directory on the WebDAV server where you want to put your files
- `$WEBDAV_USER`: name of user authorized to upload
- `$WEBDAV_PASSWORD`: user's password
- `$WEBDAV_RELEASE_NAME`: name of the release directory (optional on *GitHub actions*)

**Note:** Secrets must not be stored inside the repository, nor be visible to end users. You need to store them securely, ideally using the credentials storage your build system provides (on GitHub actions, there's *Secrets*, for instance).


## Changelog Generation
`pyuploadtool` support Changelog generation, which is optional, and can be enabled with the `CHANGELOG_TYPE` environment variable.
```bash
CHANGELOG_TYPE=standard ./pyuploadtool*.AppImage
```

### Changelog Types
`CHANGELOG_TYPE` can have any of the following values:
* `CHANGELOG_TYPE=none`, to disable generating Changelog (default)
* `CHANGELOG_TYPE=standard`, Standard Changelog
* `CHANGELOG_TYPE=conventional`, Conventional changelog, follows the [Conventional Commit Spec](https://www.conventionalcommits.org/) which classifies your commits as Features, Bug Fixes, etc, provided your commits follow the spec.

By default, `CHANGELOG_TYPE` is `none` unless explicitly specified.
