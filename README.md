# pyuploadtool

A build-system-agnostic tool for creating releases and uploading artifacts on various hosting providers.

*Inspired by [uploadtool](https://github.com/probonopd/uploadtool), but much better in so many ways...*


## Usage

Using this tool is fairly straightforward. Ideally, in one of the supported build environments, all you have to do is to run it! The tool figures out its configuration from the environment variables (which either are provided by the build system, or set by the user).

Please see the following sections for more information on how to use the tool with the supported build systems and release hosting providers.


## Supported build systems

This tool supports various build systems. Build system implementations are used to read metadata about a release from the environment, e.g., by processing available environment variables.

### GitHub actions

To use the tool with [GitHub actions](https://docs.github.com/en/free-pro-team@latest/github/administering-a-repository/about-releases), all you have to do is to provide `GITHUB_TOKEN` in the environment of your upload step.

The tool will by default upload files to *GitHub releases*.

An example pipeline step look like this:

```
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

```
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


### WebDAV

You can upload to any WebDAV server which supports `PUT` operations. The following environment variables need to be set:

- `$WEBDAV_URL`: URL to the directory on the WebDAV server where you want to put your files
- `$WEBDAV_USER`: name of user authorized to upload
- `$WEBDAV_PASSWORD`: user's password
- `$WEBDAV_RELEASE_NAME`: name of the release directory (optional on *GitHub actions*)

**Note:** Secrets must not be stored inside the repository, nor be visible to end users. You need to store them securely, ideally using the credentials storage your build system provides (on GitHub actions, there's *Secrets*, for instance).
