# Data Circle Tracking - GTM Web Tag Template

A Google Tag Manager **web** tag template for the [Data Circle](https://data-circle.notion.site/) tracking tag (`crcl` / `edi5on.com` loader). It loads the tag, tracks page views automatically (including SPA route changes), and sends custom events such as `add_to_cart` and `purchase`.

This is a **client-side** integration. Data Circle delivers events with `navigator.sendBeacon` to `https://edi5on.com`, so no server-side (sGTM) container is required.

## Features

- **Configuration tag**: loads the Data Circle tag and tracks page views / SPA navigation automatically.
- **Custom event tag**: send any Data Circle event (`purchase`, `add_to_cart`, `view_item`, `begin_checkout`, ...) with arbitrary key/value parameters.
- **Default parameters**: attach values to every event (via the Data Circle `set` command, e.g. `currency`, `user_id`).
- Uses a proper command queue (`createArgumentsQueue`) so events fired before the loader finishes are buffered and not lost.
- Optional console debug logging.

## How It Works

Data Circle exposes a `crcl()` command queue, identical in shape to the native snippet:

```html
<script async src="https://edi5on.com/<your-uuid>.js"></script>
<script>
  window.crclEvents = window.crclEvents || [];
  function crcl() { crclEvents.push(arguments); }
  crcl("config", "<your-uuid>");
</script>
```

This template recreates that queue inside the GTM sandbox and:

1. **Configuration tag**: queues `set` defaults (if any), then `config`, then injects the loader. Page views are tracked automatically.
2. **Custom event tag**: queues `crcl("event", "<name>", { ...params })` and ensures the loader is present (loaded once per account via a shared cache token).

## Installation

### From the Community Template Gallery

1. In your GTM container, go to **Templates** > **Tag Templates** > **Search Gallery**
2. Search for **Data Circle Tracking**
3. Click **Add to workspace**

### Manual Installation

1. Download `template.tpl` from this repository
2. In GTM, go to **Templates** > **New**
3. Click the three-dot menu > **Import**
4. Select the downloaded file

## Setup Guide

You need one Configuration tag and one Custom event tag per interaction you track.

### Tag 1: Configuration (loader + page views)

1. Create a new tag using the **Data Circle Tracking** template
2. Set **Tag type** to "Configuration (loader + page views)"
3. Enter your **Config ID (UUID)** (provided by your Data Circle Account Manager)
4. (Optional) Add **Default parameters** such as `currency` = `EUR`
5. Set the trigger to **All Pages**

> If you already load the Data Circle snippet in your site theme, you can skip this tag. It is only needed if you want GTM to load the tag for you.

### Tag 2: Custom event (e.g. purchase)

1. Create a new tag using the **Data Circle Tracking** template
2. Set **Tag type** to "Custom event"
3. Enter the same **Config ID (UUID)**
4. Set **Event name** to the Data Circle event name, e.g. `purchase` (not `purchase_stape`)
5. Add **Event parameters**, referencing GTM variables in the Value column:

| Parameter name | Example value |
|----------------|---------------|
| `transaction_id` | `{{DLV - ecommerce.transaction_id}}` |
| `value` | `{{DLV - ecommerce.value}}` |
| `tax` | `{{DLV - ecommerce.tax}}` |
| `shipping` | `{{DLV - ecommerce.shipping}}` |
| `currency` | `EUR` |

6. Set the trigger to your purchase Custom Event trigger

For `add_to_cart`, use parameters `item_id`, `item_name`, `price`, `currency`, `quantity`.

## Field Reference

| Field | Applies to | Required | Description |
|-------|-----------|----------|-------------|
| Tag type | both | yes | Configuration or Custom event |
| Config ID (UUID) | both | yes | Your Data Circle account UUID |
| Default parameters | config | no | Sent with every event via `set` |
| Event name | event | yes | Data Circle event name |
| Event parameters | event | no | Key/value parameters for the event |
| Log to console | both | no | Debug logging |

## Permissions

- **Inject scripts**: `https://edi5on.com/*` (the Data Circle loader)
- **Access globals**: `crcl` (read/write/execute), `crclEvents` (read/write) for the command queue
- **Logging**: console logging in debug/preview only

## Privacy

Per the Data Circle documentation, for a classic configuration in France (no unique ID / pseudonymous or personal data), the tag is designed to meet the CNIL audience-measurement exemption. Confirm your own configuration and obligations.

## Resources

- [Data Circle implementation guide](https://data-circle.notion.site/Guide-d-impl-mentation-du-tag-920379358906481687379959b6c35d4c)

## Author

Built and maintained by [New North Digital](https://newnorth.nl).

## License

Apache License 2.0. See [LICENSE](LICENSE).
