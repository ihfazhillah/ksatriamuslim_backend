(function(global, factory) {
    if (typeof exports === 'object' && typeof exports.nodeName !== 'string') { // CJS
      factory(exports);
    } else if (typeof define === 'function' && define.amd) { // AMD
      define(['exports'], factory);
    } else { // Browser
      global = typeof globalThis !== 'undefined' ? globalThis : global || self;
      factory(global['loomEmbed'] = {});
    }
  }(typeof self !== 'undefined' ? self : this, function (exports) {
  
var __defProp = Object.defineProperty;
var __defProps = Object.defineProperties;
var __getOwnPropDescs = Object.getOwnPropertyDescriptors;
var __getOwnPropSymbols = Object.getOwnPropertySymbols;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __propIsEnum = Object.prototype.propertyIsEnumerable;
var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
var __spreadValues = (a, b) => {
  for (var prop in b || (b = {}))
    if (__hasOwnProp.call(b, prop))
      __defNormalProp(a, prop, b[prop]);
  if (__getOwnPropSymbols)
    for (var prop of __getOwnPropSymbols(b)) {
      if (__propIsEnum.call(b, prop))
        __defNormalProp(a, prop, b[prop]);
    }
  return a;
};
var __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));
var __markAsModule = (target) => __defProp(target, "__esModule", { value: true });
var __export = (target, all) => {
  __markAsModule(target);
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};

// src/index.ts
__export(exports, {
  gifEmbed: () => gifEmbed,
  linkReplace: () => linkReplace,
  oembed: () => oembed,
  textReplace: () => textReplace,
  validate: () => validate_default
});

// src/common.ts
var LOOM_BASE_REGEX_STR = "(?:https?://)?((?:stage.loom.com|loom.com|www.loom.com|loomlocal.com:4444)/share/[a-f0-9]+)";
var LOOM_URL_REGEX = new RegExp(`^${LOOM_BASE_REGEX_STR}$`);
var LOOM_URL_MATCH_REGEX = new RegExp(`${LOOM_BASE_REGEX_STR}`, "g");
var LOOM_HOSTNAME_CAPTURE = /(www\.loom\.com|loom\.com|stage\.loom\.com|loomlocal\.com:4444)/i;
var LINK_REPLACED_CLASS = "lo-link-replaced";

// src/validate.ts
var isLoomUrl = (url) => LOOM_URL_REGEX.test(url);
var isValidEmbedUrl = (url) => isLoomUrl(url);
var isValidLinkNode = (node) => !node.className.includes(LINK_REPLACED_CLASS) && isValidEmbedUrl(node.href);
var validate_default = {
  isLoomUrl
};

// src/oembed.ts
var SRC_URL_REGEX = /src=["']+(https?:\/\/[a-zA-z\d:\.\/?&]+)/;
var getResponsiveEmbedCode = (embedURL, heightAspectRatio) => {
  const padding = `${heightAspectRatio * 100}%`;
  const wrapperStyles = `position: relative; padding-bottom: ${padding}; height: 0;`;
  const iframeStyles = "position: absolute; top: 0; left: 0; width: 100%; height: 100%;";
  const staticAttributes = 'frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen';
  return `
<div class="lo-emb-vid" style="${wrapperStyles}">
  <iframe src="${embedURL}" style="${iframeStyles}" ${staticAttributes}></iframe>
</div>`.split("\n").map((s) => s.trim()).join("");
};
var chooseAspectRatio = (data) => {
  const { width, height } = data;
  if (width == null || height == null) {
    return 1080 / 1920;
  }
  return height / width;
};
var enhanceEmbedCode = (videoData, options) => {
  const { width, height } = options;
  if (!width && !height) {
    const [, embedUrl] = videoData.html.match(SRC_URL_REGEX);
    const aspectRatio = chooseAspectRatio(videoData);
    return __spreadProps(__spreadValues({}, videoData), {
      html: getResponsiveEmbedCode(embedUrl, aspectRatio)
    });
  }
  return videoData;
};
var buildLoomOembedUrl = (url, options) => {
  const { width, height, gifThumbnail, hideOwner } = options;
  const maxWidth = width ? `&maxwidth=${width}` : "";
  const maxHeight = height ? `&maxheight=${height}` : "";
  const gifParam = gifThumbnail ? `&gif=${gifThumbnail}` : "";
  const ownerParam = hideOwner ? `&hide_owner=${hideOwner}` : "";
  const [loomDomain] = url.match(LOOM_HOSTNAME_CAPTURE);
  let loomBaseDomain = loomDomain;
  if (loomDomain === "loom.com") {
    loomBaseDomain = `www.${loomDomain}`;
  }
  return `https://${loomBaseDomain}/v1/oembed?url=${url}${maxWidth}${maxHeight}${gifParam}${ownerParam}`;
};
var oembed = (linkUrl, options = {}) => {
  const isSupportedUrl = isValidEmbedUrl(linkUrl);
  if (isSupportedUrl) {
    return fetch(buildLoomOembedUrl(linkUrl, options)).then((resp) => resp.json()).then((videoData) => enhanceEmbedCode(videoData, options)).catch((e) => {
      throw new Error("Unable to fetch oembed data:" + e);
    });
  }
  throw new Error("URL is not from a supported video provider");
};
var gifEmbed = async (linkUrl) => {
  const oEmbed = await oembed(linkUrl, { gifThumbnail: true });
  return `<a href="${linkUrl}">
    <img style="max-width:300px;" src="${oEmbed.thumbnail_url}">
  </a>`;
};

// src/linkReplace.ts
var createNodeFromString = (htmlString) => {
  const containerNode = document.createElement("div");
  containerNode.innerHTML = htmlString;
  return containerNode.firstChild;
};
var injectVideo = (linkNode, embedString) => {
  const embedNode = createNodeFromString(embedString);
  if (embedNode && linkNode.parentNode) {
    linkNode.parentNode.insertBefore(embedNode, linkNode);
  }
};
var linkReplace = (selector = "a", options = {}, target = document) => {
  const linkNodes = [
    ...Array.from(target.querySelectorAll(selector))
  ];
  linkNodes.filter((item) => isValidLinkNode(item)).forEach(async (node) => {
    const { html } = await oembed(node.href, options);
    injectVideo(node, html);
    node.className = `${node.className} ${LINK_REPLACED_CLASS}`;
    return true;
  });
};

// src/textReplace.ts
var normalizeUrls = (url) => {
  const [, loomBaseUrl] = url.match(LOOM_URL_REGEX);
  return {
    originalUrl: url,
    requestUrl: `https://${loomBaseUrl}`
  };
};
var textReplace = async (textString, options = {}) => {
  const textInput = textString || "";
  const loomMatches = textInput.match(LOOM_URL_MATCH_REGEX);
  if (!loomMatches) {
    return textInput;
  }
  const embedPromises = loomMatches.map(normalizeUrls).map(async (urls) => {
    const { html } = await oembed(urls.requestUrl, options);
    return __spreadProps(__spreadValues({}, urls), {
      embedCode: html
    });
  });
  const embedData = await Promise.all(embedPromises);
  return embedData.reduce((acc, curr) => {
    const { originalUrl, embedCode } = curr;
    const urlReplaceRegex = new RegExp(originalUrl, "g");
    return acc.replace(urlReplaceRegex, embedCode);
  }, textInput);
};

}));
//# sourceMappingURL=index.js.map
