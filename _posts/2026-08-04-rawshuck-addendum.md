---
title: 'Rawshuck — an addendum'
subtitle: 'A couple of new patches — and the strange case of the vanishing JPEG files'
date: 2026-08-04
permalink: /posts/2026/08/rawshuck-addendum/
excerpt: 'All I wanted was to delete some RAW files. iCloud continues to have other ideas.'
tags:
  - photography
  - coding
  - tools
  - icloud
---

_Rawshuck lives at [rawshuck.pages.dev](https://rawshuck.pages.dev/). This post is an addendum to the original backstory [here](https://macklin-cordes.com/posts/2026/08/rawshuck/)._

A few days ago, I released my new app, _Rawshuck_. It's a small, simple tool with one function and one function only: speedy culling of RAW+JPEG photo libraries.

Long story short, I shoot in RAW+JPEG mode on a Canon R10. JPEGs are perfectly fine for the vast majority of pictures, but I want to retain the RAWs for my best shots. I wanted to be able to sort my photos into one of three fates: i) keep the RAW+JPEG pair (true bangers only), ii) keep the JPEG, ditch the RAW (most pics), iii) delete altogether (duds). This ended up being surprisingly painful, at least in the native Apple ecosystem, so I wrote my own little app to do it.

In this addendum, I want to share the story of a bizarre bug I encountered after the app's initial release, the tedious process of troubleshooting it, and the eventual fix.

## So, where were we?

Having solved the first weird bug, the case of the resurrected RAWs, I set about the task of sorting my back catalogue in earnest. Exported a couple of hundred pictures, culled them, deleted the originals, emptied Recently Deleted, dragged the survivors back into Photos. The import window came up, flashed a number that looked right, and then the list would suddenly collapse to about a third of that. No error or warning. Just a literal split second where everything seemed fine, then 2/3 of the pictures vanishing in a flash.

I worked out that, in every case, the disappearing pictures were JPEGs that Rawshuck had marked (the workaround for avoiding resurrected RAWs). Not ideal.

## Wall Three: Vanishing imports

The obvious suspect was the marking mechanism, so I started by comparing the byte structure of a marked JPEG vs an untouched one. There I found something awkward. A Canon JPEG isn't one image — it's two. After the main 6000×4000 photo ends, Canon appends a second, smaller JPEG (1620×1080), a screen-sized preview so that cameras, printers and preview panes can show you the shot without decoding the full 24-megapixel image. A little table near the front of the file, in a segment called MPF, records where that second image lives, as a byte offset.

Rawshuck v1.0.0 would insert its 51-byte tag *in the middle of the file*, after the MPF table but before the preview image it points to. Which meant every offset in the table was now 51 bytes wrong. In practice, this doesn't matter too much. It only affects certain software that would want to make use of that second smaller image for preview purposes, and even then, the software would just decode the full image as a fallback to get its preview — a little inefficient, but nothing really breaks at the user end.

Still, I'd prefer not to break JPEG files like this. So I patched it up. Rawshuck v1.1 appends a small tag at the very end of the file. It achieves the trick of making the JPEG non-byte-identical to the original so Photos doesn't raise its RAW from the grave, but doesn't mess with the MPF table any more.

Great. So this might fix the weird import issue too, right...?

No.

Same issue. A brief flash of hope, then instant collapse.

The MPF bug was real, so I'm glad I found it and fixed it. But the correlation with the disappearing import issue was a coincidence. So the detective work continued.

What followed was a series of elaborate tests. Try importing one at a time: fine. Two at a time? Also fine. All of them? No. Split the batch in half... Fine. Maybe it's a size issue then? Oh nope, never mind, the second half didn't work. Importing JPEGs only, without the RAW counterparts, that worked fine. That was the weird thing — I already had evidence that, once you did import the JPEGs one way or another, they were perfectly ok. It's not like they were corrupted or anything. It was just a weird glitch with the import process in the app.

I tried importing a different batch of photos... Bizarrely, that batch had the same vanishing issue the first time, but when I cancelled the import and tried *the exact same* drag-and-drop action again, it suddenly worked.

I was pretty much ready to accept this as an unsolvable mystery of the Apple Photos black box, and resign myself to just checking carefully that the number of photos imported was the number I expected on each batch, reimporting just the JPEGs a second time if necessary. And then...

## The log was right there the entire time

I belatedly learned that Photos writes to the macOS unified log. I could simply ask it what it thought it was doing!

```
18:58:04.170  RECEIVED:(aevt,odoc) ...
18:58:04.429  Created source for 'temp_photos' containing 94 URL(s)
18:58:04.583  PHImportUrlSource loaded 94 assets

18:58:04.850  RECEIVED:(aevt,odoc) ...          ← a second event
18:58:05.115  Created source for 'temp_photos' containing 93 URL(s)
18:58:05.519  PHImportUrlSource loaded 61 assets
```

94 URLs, 93 URLs, 187 files total, which was exactly my problematic batch, sliced in two.

When you select a large number of files in Finder and drag them onto an app, macOS delivers them as an "open documents" AppleEvent — and in this case, it was sending more than one. Photos builds a separate import source for each event. The import events were working fine, no errors, but it was basically treating it as if I was clicking and dragging the first 94 files, then clicking and dragging the other 93 separately. And then the Import pane would show only the last one instead of the union of the two.

## But why?

It raises the question: why was the cut always in the same place, marked JPEGs in one batch and all the rest in the other? It wasn't a filename or size issue — it would always slice the batch into those two groups, regardless of how the files were ordered.

Finally, I found the culprit, in metadata hidden in the extended attributes of each file.

```
unmarked file:  com.apple.cscachefs
                com.apple.lastuseddate#PS
                com.apple.quarantine: 0082;6a6fd622;Photos;
marked file:    com.apple.lastuseddate#PS
```

When Photos exports originals, it adds a quarantine flag to each file. It's the kind of flag that gets added to files downloaded from the internet, so it can ask "are you sure you want to open this?"

The Rawshuck JPEG-marking script, in the course of writing the tag, would rebuild the file from a temporary copy, scrubbing the extended attributes. Every marked JPEG lost its quarantine flag. Every untouched JPEG and every RAW kept it.

macOS was sorting my drag into quarantined and non-quarantined items and sending each group as its own event, because quarantined files take a different route when they're opened. Photos then displayed the second group and discarded the first, and 94 photographs would disappear from the screen due to a security flag I didn't know existed.

Confirmation took ten seconds. Strip the flag from everything so the folder is uniform again:

```
xattr -r -d com.apple.quarantine .
```

Et voilà. All 155 photos (=187 total files, with the RAW+JPEG pairs I kept) appeared in the Photos Import pane. First time. I still can't fully explain the inconsistent behaviour I observed (particularly the batch that didn't work, then worked fine for some reason). But it's as close to a smoking gun as I'll get.

After all this, there was one final sick joke. I realised that, if you drag a *folder* into Photos (rather than Cmd+A selecting and dragging all the individual files), it'll treat it as one import event and work perfectly fine.

## The patch

Rawshuck v1.1.1 no longer rebuilds the JPEG from a temp copy, and thus no longer strips the extended attributes and quarantine flag. So this should be fixed at the source. The thing is, there was never any need to rebuild an entire ~10MB file just to add a 51-byte tag on the end anyway. You can simply open it and append, which leaves the inode, the extended attributes and the quarantine flag exactly where they were.

The reason for the initial design is slightly more elegant handling if the commit process gets interrupted or crashes for some reason. The trade-off is that now, if the computer were to crash right as the commit process was doing its thing, there's a chance that it could leave a truncated tag at the end of the JPEG. I can hardly think of an instance where this would matter, since the main point of the tag is simply to make the JPEG ever so slightly non-byte-identical to the original. The only case I can think of is, if you wanted to search for all marked JPEGs for some reason, and you did so by searching file metadata for "photo-cull" (the format of the tag is `photo-cull:(random alphanumeric text string)`), then the affected JPEG wouldn't show up if it got cut off at "photo-cu" or something like that. But at any rate, it would be fixed by simply re-committing the photo in Rawshuck after the crash anyway.

To be perfectly honest, the temp copy > re-write step was heavy-handed and over-engineered by an over-eager coding agent. It wasn't _bad_ per se — write-to-temp-then-atomically-replace is the textbook way to modify a file without risking a half-written result if the process dies. But in this case it was excessive. And an upshot of the new method is that now it just writes ~50 bytes per file, instead of re-writing the full ~10MB JPEG for every picture, so it's much less intensive on your disk and much faster. There's a small lesson there.

## Current state of play

Rawshuck v1.1.1 marks JPEGs at the very end of the file, where it can't shift anything, and appends in place so nothing about the file's metadata changes either.

For any JPEGs already marked the old way, it's possible to run the `mark-jpeg.py` script with a `--repair` flag, and it carries the extended attributes across. Almost certainly unnecessary from a practical perspective (I'm not bothering to run it on my previous batches myself), but it's there for completeness.

Going forward, when reimporting after culling some back catalogue, I would recommend dragging the *folder* of pictures, rather than selecting and dragging all the files within it. In theory it no longer matters, but it would prevent any unforeseen future issues with other file types. And of course, take good care to ensure you've reimported everything successfully before deleting anything from a staging folder or clearing an SD card — but that would've been wise to do anyway ;)

## Links

Rawshuck is free, and lives at [rawshuck.pages.dev](https://rawshuck.pages.dev/).

The code (web and Python versions, plus a standalone JPEG-marking utility) is open source (GPL v3) on [GitHub](https://github.com/JaydenM-C/rawshuck). Bug reports welcome — and if you shoot a non-Canon camera, sample RAW files are welcome via GitHub issues so I can add embedded-preview support for more formats. (There is already some in-built support for non-Canon brand-specific file types but they're untested.)

If you find it useful and feel like chipping in a few quid toward ongoing development, my [Ko-fi page](https://ko-fi.com/jaydenmacklincordes) is here.

Once you've sorted some nice photos, you might like to extract some beautiful, naturalistic colour palettes from them using my [Chromatography](https://chromatography.pages.dev) web app. Read about Chromatography [here](https://macklin-cordes.com/posts/2026/04/chromatography/).

