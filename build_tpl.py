#!/usr/bin/env python3
# Assembles template.tpl, injecting the base64 thumbnail from thumb.b64.
thumb = open('thumb.b64').read().strip()
data_uri = 'data:image/png;base64,' + thumb

TPL = r'''___TERMS_OF_SERVICE___

By creating or modifying this file you agree to Google Tag Manager's Community
Template Gallery Developer Terms of Service available at
https://developers.google.com/tag-manager/gallery-tos (or such other URL as
Google may provide), as modified from time to time.


___INFO___

{
  "type": "TAG",
  "id": "cvt_temp_public_id",
  "version": 1,
  "securityGroups": [],
  "displayName": "Data Circle Tracking",
  "categories": [
    "ANALYTICS",
    "ATTRIBUTION",
    "CONVERSIONS"
  ],
  "brand": {
    "id": "brand_dummy",
    "displayName": "New North Digital",
    "thumbnail": "__THUMB__"
  },
  "description": "Data Circle tracking tag. Loads the tag (page views + SPA auto-tracking) and sends custom events such as add_to_cart and purchase via the crcl command queue. Client-side, no server container needed.",
  "containerContexts": [
    "WEB"
  ]
}


___TEMPLATE_PARAMETERS___

[
  {
    "type": "SELECT",
    "name": "actionType",
    "displayName": "Tag type",
    "macrosInSelect": false,
    "selectItems": [
      {
        "value": "config",
        "displayValue": "Configuration (loader + page views)"
      },
      {
        "value": "event",
        "displayValue": "Custom event"
      }
    ],
    "simpleValueType": true,
    "help": "Choose \"Configuration\" once, firing on All Pages: it loads the Data Circle tag and tracks page views automatically (including SPA route changes). Choose \"Custom event\" for each interaction you want to send, such as add_to_cart or purchase."
  },
  {
    "type": "TEXT",
    "name": "configId",
    "displayName": "Config ID (UUID)",
    "simpleValueType": true,
    "valueValidators": [
      {
        "type": "NON_EMPTY"
      }
    ],
    "help": "The UUID provided by your Data Circle Account Manager, e.g. 00000000-0000-0000-0000-000000000000. Used to load the tag and route events to your account.",
    "alwaysInSummary": true
  },
  {
    "type": "SIMPLE_TABLE",
    "name": "defaultParams",
    "displayName": "Default parameters (sent with every event)",
    "simpleTableColumns": [
      {
        "defaultValue": "",
        "displayName": "Parameter name",
        "name": "name",
        "type": "TEXT"
      },
      {
        "defaultValue": "",
        "displayName": "Value",
        "name": "value",
        "type": "TEXT"
      }
    ],
    "newRowButtonText": "Add default parameter",
    "help": "Optional. Applied via the Data Circle \"set\" command before \"config\", so these are attached to every event (e.g. currency = EUR, user_id).",
    "enablingConditions": [
      {
        "paramName": "actionType",
        "paramValue": "config",
        "type": "EQUALS"
      }
    ]
  },
  {
    "type": "TEXT",
    "name": "eventName",
    "displayName": "Event name",
    "simpleValueType": true,
    "valueValidators": [
      {
        "type": "NON_EMPTY"
      }
    ],
    "help": "The Data Circle event name. Use the names from the Data Circle docs, e.g. purchase, add_to_cart, view_item, begin_checkout. Note: it is \"purchase\", not \"purchase_stape\".",
    "enablingConditions": [
      {
        "paramName": "actionType",
        "paramValue": "event",
        "type": "EQUALS"
      }
    ],
    "alwaysInSummary": true
  },
  {
    "type": "SIMPLE_TABLE",
    "name": "eventParams",
    "displayName": "Event parameters",
    "simpleTableColumns": [
      {
        "defaultValue": "",
        "displayName": "Parameter name",
        "name": "name",
        "type": "TEXT"
      },
      {
        "defaultValue": "",
        "displayName": "Value",
        "name": "value",
        "type": "TEXT"
      }
    ],
    "newRowButtonText": "Add parameter",
    "help": "Optional key/value parameters for this event. For purchase: transaction_id, value, tax, shipping, currency. For add_to_cart: item_id, item_name, price, currency, quantity. Reference GTM variables in the Value column.",
    "enablingConditions": [
      {
        "paramName": "actionType",
        "paramValue": "event",
        "type": "EQUALS"
      }
    ]
  },
  {
    "type": "GROUP",
    "name": "debugGroup",
    "displayName": "Debugging",
    "groupStyle": "ZIPPY_CLOSED",
    "subParams": [
      {
        "type": "CHECKBOX",
        "name": "debug",
        "checkboxText": "Log to console for debugging",
        "simpleValueType": true
      }
    ]
  }
]


___SANDBOXED_JS_FOR_WEB_TEMPLATE___

const log = require('logToConsole');
const injectScript = require('injectScript');
const copyFromWindow = require('copyFromWindow');
const createArgumentsQueue = require('createArgumentsQueue');
const callInWindow = require('callInWindow');
const getType = require('getType');
const makeTableMap = require('makeTableMap');
const makeString = require('makeString');

const LOADER_HOST = 'https://edi5on.com/';
const FN = 'crcl';
const QUEUE = 'crclEvents';

const actionType = data.actionType;
const enableDebug = data.debug;

const debugLog = (msg) => {
  if (enableDebug) {
    log('Data Circle GTM - ' + msg);
  }
};

debugLog('Starting with tag type: ' + actionType);

const configId = data.configId;
if (!configId) {
  debugLog('Error: Config ID (UUID) is required');
  data.gtmOnFailure();
  return;
}

// Ensure the crcl command queue exists, mirroring the native Data Circle snippet
// (a global crclEvents array plus a crcl() function that pushes its arguments onto it).
// The loader replaces the array's push method to drain queued commands once it loads,
// so pushing commands before the loader has finished loading is safe and order-preserving.
if (getType(copyFromWindow(FN)) !== 'function') {
  createArgumentsQueue(FN, QUEUE);
}

if (actionType === 'config') {
  if (data.defaultParams && data.defaultParams.length > 0) {
    const defaults = makeTableMap(data.defaultParams, 'name', 'value');
    if (defaults) {
      // "set" must be queued before "config"
      callInWindow(FN, 'set', defaults);
      debugLog('Queued set defaults');
    }
  }
  callInWindow(FN, 'config', makeString(configId));
  debugLog('Queued config: ' + configId);
} else if (actionType === 'event') {
  const eventName = data.eventName;
  if (!eventName) {
    debugLog('Error: Event name is required');
    data.gtmOnFailure();
    return;
  }
  if (data.eventParams && data.eventParams.length > 0) {
    const params = makeTableMap(data.eventParams, 'name', 'value');
    callInWindow(FN, 'event', eventName, params ? params : {});
  } else {
    callInWindow(FN, 'event', eventName, {});
  }
  debugLog('Queued event: ' + eventName);
} else {
  debugLog('Unknown tag type: ' + actionType);
  data.gtmOnFailure();
  return;
}

// Load the Data Circle loader. The cache token is keyed on the config ID, so the
// script loads only once per account even when many tags reference it.
const loaderUrl = LOADER_HOST + makeString(configId) + '.js';
injectScript(loaderUrl, data.gtmOnSuccess, data.gtmOnFailure, 'datacircle-' + makeString(configId));


___WEB_PERMISSIONS___

[
  {
    "instance": {
      "key": {
        "publicId": "logging",
        "versionId": "1"
      },
      "param": [
        {
          "key": "environments",
          "value": {
            "type": 1,
            "string": "debug"
          }
        }
      ]
    },
    "clientAnnotations": {
      "isEditedByUser": true
    },
    "isRequired": true
  },
  {
    "instance": {
      "key": {
        "publicId": "access_globals",
        "versionId": "1"
      },
      "param": [
        {
          "key": "keys",
          "value": {
            "type": 2,
            "listItem": [
              {
                "type": 3,
                "mapKey": [
                  {"type": 1, "string": "key"},
                  {"type": 1, "string": "read"},
                  {"type": 1, "string": "write"},
                  {"type": 1, "string": "execute"}
                ],
                "mapValue": [
                  {"type": 1, "string": "crcl"},
                  {"type": 8, "boolean": true},
                  {"type": 8, "boolean": true},
                  {"type": 8, "boolean": true}
                ]
              },
              {
                "type": 3,
                "mapKey": [
                  {"type": 1, "string": "key"},
                  {"type": 1, "string": "read"},
                  {"type": 1, "string": "write"},
                  {"type": 1, "string": "execute"}
                ],
                "mapValue": [
                  {"type": 1, "string": "crclEvents"},
                  {"type": 8, "boolean": true},
                  {"type": 8, "boolean": true},
                  {"type": 8, "boolean": false}
                ]
              }
            ]
          }
        }
      ]
    },
    "clientAnnotations": {
      "isEditedByUser": true
    },
    "isRequired": true
  },
  {
    "instance": {
      "key": {
        "publicId": "inject_script",
        "versionId": "1"
      },
      "param": [
        {
          "key": "urls",
          "value": {
            "type": 2,
            "listItem": [
              {
                "type": 1,
                "string": "https://edi5on.com/*"
              }
            ]
          }
        }
      ]
    },
    "clientAnnotations": {
      "isEditedByUser": true
    },
    "isRequired": true
  }
]


___TESTS___

scenarios:
- name: Config - injects loader and calls config
  code: |-
    const mockData = {
      actionType: 'config',
      configId: '019df2aa-fd34-713a-bfce-f5118a4eb4f6',
      debug: false
    };

    mock('injectScript', function(url, onSuccess, onFailure, cacheToken) {
      onSuccess();
    });

    runCode(mockData);

    assertApi('createArgumentsQueue').wasCalled();
    assertApi('injectScript').wasCalled();
    assertApi('callInWindow').wasCalled();
    assertApi('gtmOnSuccess').wasCalled();
- name: Config - queues crcl before injecting loader
  code: |-
    const getType = require('getType');
    const copyFromWindow = require('copyFromWindow');

    const mockData = {
      actionType: 'config',
      configId: '019df2aa-fd34-713a-bfce-f5118a4eb4f6',
      debug: false
    };

    let fnDefinedAtInject = false;
    mock('injectScript', function(url, onSuccess, onFailure, cacheToken) {
      fnDefinedAtInject = getType(copyFromWindow('crcl')) === 'function';
      onSuccess();
    });

    runCode(mockData);

    assertThat(fnDefinedAtInject).isEqualTo(true);
    assertApi('gtmOnSuccess').wasCalled();
- name: Config - fails without config ID
  code: |-
    const mockData = {
      actionType: 'config',
      configId: '',
      debug: false
    };

    mock('injectScript', function(url, onSuccess, onFailure, cacheToken) {
      onSuccess();
    });

    runCode(mockData);

    assertApi('gtmOnFailure').wasCalled();
- name: Event - sends a custom event with parameters
  code: |-
    const mockData = {
      actionType: 'event',
      configId: '019df2aa-fd34-713a-bfce-f5118a4eb4f6',
      eventName: 'purchase',
      eventParams: [
        {name: 'transaction_id', value: 'T12345'},
        {name: 'value', value: '10.42'},
        {name: 'currency', value: 'EUR'}
      ],
      debug: false
    };

    mock('injectScript', function(url, onSuccess, onFailure, cacheToken) {
      onSuccess();
    });

    runCode(mockData);

    assertApi('callInWindow').wasCalled();
    assertApi('gtmOnSuccess').wasCalled();
- name: Event - sends a custom event without parameters
  code: |-
    const mockData = {
      actionType: 'event',
      configId: '019df2aa-fd34-713a-bfce-f5118a4eb4f6',
      eventName: 'view_item',
      debug: false
    };

    mock('injectScript', function(url, onSuccess, onFailure, cacheToken) {
      onSuccess();
    });

    runCode(mockData);

    assertApi('callInWindow').wasCalled();
    assertApi('gtmOnSuccess').wasCalled();
- name: Event - fails without an event name
  code: |-
    const mockData = {
      actionType: 'event',
      configId: '019df2aa-fd34-713a-bfce-f5118a4eb4f6',
      eventName: '',
      debug: false
    };

    mock('injectScript', function(url, onSuccess, onFailure, cacheToken) {
      onSuccess();
    });

    runCode(mockData);

    assertApi('gtmOnFailure').wasCalled();
- name: Loader failure - calls gtmOnFailure
  code: |-
    const mockData = {
      actionType: 'config',
      configId: '019df2aa-fd34-713a-bfce-f5118a4eb4f6',
      debug: false
    };

    mock('injectScript', function(url, onSuccess, onFailure, cacheToken) {
      onFailure();
    });

    runCode(mockData);

    assertApi('gtmOnFailure').wasCalled();


___NOTES___

Created on 2026-06-02 by New North Digital (newnorth.digital).
'''

TPL = TPL.replace('__THUMB__', data_uri)
open('template.tpl', 'w').write(TPL)
print('template.tpl written:', len(TPL), 'bytes')
