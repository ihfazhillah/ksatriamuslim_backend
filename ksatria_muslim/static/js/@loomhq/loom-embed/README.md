[![npm version](https://img.shields.io/npm/v/@loomhq/loom-embed)](https://www.npmjs.com/package/@loomhq/loom-embed)
[![CircleCI](https://img.shields.io/circleci/build/gh/loomhq/platform?token=510d0d800cbfbb8c1757c8e1705472c5d1c81238)](https://app.circleci.com/pipelines/github/loomhq/platform/2351/workflows/54eaa124-7378-48ac-80a7-a83ee3195322)
[![codecov](https://img.shields.io/badge/CodeCoverage-90%25-green)]()

## Installing

### npm package

```sh
npm install @loomhq/loom-embed
```

### Script tag
```html
<script type="module"> import * as loom from "https://www.unpkg.com/@loomhq/loom-embed@1.2.4/dist/esm/index.js?module"; </script>
```

See [documentation](https://dev.loom.com/docs/embed-sdk/getting-started) for installation and usage.

## Usage

```js
import * as loom from '@loomhq/loom-embed';
````

## Methods

### .linkReplace(selector, [options], target)

Replaces any loom links at the nodes matching the selector with the embedded video. Replacement occurs on the entire document, or on the optional target DOM element.

### .textReplace(textString, [options])

Takes a string and replaces any Loom URLs with the embed html

_-> returns a promise_

### .oembed(videoUrl, [options])

oembed metadata from the given video url

_-> returns a promise_

## Options

**The embed code is responsive by default. Only set the width/height values if you require your embed code to be a fixed size**

`width` - [Number] value specifying the max pixel width

`height` - [Number] value specifying the max pixel height
