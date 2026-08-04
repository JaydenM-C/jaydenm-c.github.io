---
Draft addendum for https://macklin-cordes.com/posts/2026/08/rawshuck/
Suggested placement: new section after "The case of the resurrected RAWs",
before "Links". Suggested tag addition: none needed.
---

## Addendum: the case of the vanishing imports

*Added [DATE]. The original post ended with me about to press `J` several thousand times. Reader, the `J` key was the least of it.*

Having solved the resurrected RAWs, I set about the back catalogue in earnest. Exported a couple of hundred pictures, culled them, deleted the originals, emptied Recently Deleted, dragged the survivors back into Photos. The import window came up, flashed a number that looked right, and then — while I watched — the list quietly collapsed to about a third of it. No error. No warning. Just fewer photos than I had a moment ago.

The missing ones were, every single time, exactly the JPEGs that Rawshuck had marked.

Well. That's a fairly incriminating look for my own software.

### Wall three, in which I accuse myself

The obvious suspect was the marking. So I went spelunking through the bytes of a marked file and a pristine one, and found something I hadn't known was there. A Canon JPEG isn't one image — it's two. After the main 6000×4000 photo ends, Canon appends a second, smaller JPEG (1620×1080), a screen-sized preview so that cameras and printers and preview panes can show you the shot without decoding twenty-four megapixels. A little table near the front of the file, in a segment called MPF, records where that second image lives, as a byte offset.

And my marking code, in v1.0.0, inserted its 51-byte tag *in the middle of the file* — after that table, before the images it points at. Which meant every offset in the table was now 51 bytes wrong. The table confidently pointed at a spot 51 bytes before the preview actually began, at four bytes of nothing in particular.

I had, in the most literal sense, broken the files. I'd shifted the furniture and not updated the map.

I checked the whole batch. Ninety-four marked files, all off by exactly −51. Sixty-one unmarked files, all exact. Zero exceptions. And ninety-four was precisely the number of photos that had gone missing from the import.

Beautiful. A perfect correlation, a plausible mechanism, and a bug that was unambiguously mine. Case closed, again.

Except it wasn't, because the correlation was a liar.

### The beautiful theory, murdered by a fact

I wrote a repair function — excise the mid-file tag, restore every offset byte-exactly, re-tag at the very end of the file where it displaces nothing — ran it over a replica of the whole batch, verified the arithmetic came out clean, and dragged the repaired files into Photos with the satisfied air of a man about to be proven right.

They collapsed in exactly the same way.

So the MPF damage was real, and it was mine, and it had nothing to do with it. It was a co-traveller: something that happened to the same files at the same time for the same reason, sitting innocently in the passenger seat while I put it on trial.

What followed was a fortnight of increasingly baroque black-box experiments. Import them alone: fine. Import two of them: fine. Import six of them next to a pair: fine. Import all of them: a third go missing. Split the batch in half: both halves import perfectly. Put the halves back together: collapse. Retry the identical drag: sometimes it heals, sometimes it doesn't. I convinced myself it was some load-dependent race condition inside Photos, wrote that up as my best guess, and mitigated it in the README with the saddest sentence a piece of documentation can contain: *check the number, and if it looks wrong, try again.*

### The log was right there the entire time

Fourteen experiments in, it belatedly occurred to me that Photos writes to the macOS unified log, and that I could simply ask it what it thought it was doing.

```
18:58:04.170  RECEIVED:(aevt,odoc) ...
18:58:04.429  Created source for 'temp_photos' containing 94 URL(s)
18:58:04.583  PHImportUrlSource loaded 94 assets

18:58:04.850  RECEIVED:(aevt,odoc) ...          ← a second event
18:58:05.115  Created source for 'temp_photos' containing 93 URL(s)
18:58:05.519  PHImportUrlSource loaded 61 assets
```

Ninety-four, then ninety-three. One hundred and eighty-seven files. My batch, exactly, sliced in two.

When you select a large number of files in Finder and drag them onto an app, macOS delivers them as an "open documents" AppleEvent — and for a big enough drag, it sends *more than one*. Photos dutifully builds a separate import source for each event. And then the Import pane shows you the last one instead of the union of them.

That's it. That's the whole thing. Nothing failed. Nothing timed out. Nothing was corrupt. There isn't a single error in the log. Photos was told about my photos twice, and it kept the second answer. The "flash" I'd been watching for a fortnight was the first chunk being displayed; the "collapse" was the second chunk replacing it.

### The actual culprit, at last

That left one question: why was the cut always in exactly the same place — right along the seam between the marked files and everything else? It survived re-sorting the folder by name. It survived re-sorting by size. Whatever macOS was slicing on, it wasn't the order I could see.

So I looked at what else was attached to these files. Not the contents this time — the metadata hanging off the side of them, the extended attributes, which I had ignored for a fortnight on the grounds that surely nothing interesting lives there.

```
unmarked file:  com.apple.cscachefs
                com.apple.lastuseddate#PS
                com.apple.quarantine: 0082;6a6fd622;Photos;
marked file:    com.apple.lastuseddate#PS
```

Photos quarantines its own exports. The same flag macOS puts on files downloaded from the internet, so it can ask "are you sure you want to open this?" — Photos stamps it on the originals it hands back to you, with its own name on the tag.

And my marking code, in the course of writing the tag, rebuilds the file from a temporary copy — which comes into the world with no extended attributes at all. Every marked JPEG lost its quarantine flag. Every untouched JPEG and every RAW kept it.

Ninety-four unquarantined files. Sixty-one quarantined JPEGs plus thirty-two quarantined RAWs — ninety-three. The two numbers in the log, precisely.

macOS was sorting my drag into quarantined and non-quarantined items and sending each group as its own event, because quarantined files take a different route when they're opened. Photos then displayed the second group and discarded the first, and I lost ninety-four photographs to a security flag I didn't know existed, being absent from files it had itself put it on, because my own program had inadvertently scrubbed it off.

The confirmation took ten seconds. Strip the flag from everything so the folder is uniform again:

```
xattr -r -d com.apple.quarantine .
```

Then the same Cmd+A drag that had failed for two weeks. All 155 photos. First time.

So the marking *was* to blame after all — but not for anything I'd suspected, and not for anything to do with JPEGs. Not the tag. Not the comment segment. Not the MPF table I'd broken and fixed. The mark's entire contribution was to remove an invisible sticker from ninety-four files and thereby make them a different *kind* of object in the eyes of the operating system's drag-and-drop machinery.

I had, twice, correctly identified that my code was at fault and then been wrong about how.

### The fix is one sentence long

**Drag the folder onto Photos, not the files inside it.**

One item. One event. One import source. Nothing to partition, whatever flags the files inside are or aren't wearing. I dragged the same batch that had failed reliably for two weeks, this time as a folder, and all 155 photos appeared at once, first time. The log shows a single event, `containing 1 URL(s)`, loading 155 assets.

I did not know whether to laugh.

(Rawshuck has stopped causing it at source, too. There was never any need to rebuild a ten-megabyte file just to add forty-nine bytes to the end of it — you can simply open it and append, which leaves the inode, the extended attributes and the quarantine flag exactly where they were. The smaller, simpler, faster operation turns out to be the one that doesn't detonate anything. On a hundred-photo batch it also stops about a gigabyte of pointless disk writes, so I'm calling that two wins and a lesson.)

### Things I have chosen to learn from this

- **Ask the software what it's doing before inferring it from the outside.** Fourteen experiments of careful behavioural detective work were beaten by one command that read the diagnostic log the system had been writing the whole time, for free, unprompted, into a buffer I could have queried on day one.
- **A perfect correlation can point at the right suspect for the wrong reason.** Ninety-four out of ninety-four, no exceptions — and it *was* causal, through a chain of five steps, not one of which could have been guessed from the outside. When I falsified the mechanism I'd imagined, I concluded the marking was innocent. It wasn't. Killing a hypothesis is not the same as clearing a suspect.
- **Two things can be true at once.** The MPF bug was real and worth fixing. It also wasn't the problem. Fixing it improved the software and changed nothing about the symptom, and both of those facts are fine.
- **The evidence isn't always in the file.** I spent a fortnight interrogating bytes — segment tables, offsets, embedded previews — while the answer sat in a scrap of metadata bolted to the outside of each file, which I'd have seen in one command on day one had it occurred to me that a file is more than its contents.
- **Beware fixes that perturb the thing you're measuring.** Marking didn't hide those photos. It quietly removed a flag from exactly the files I was studying, thereby dividing my own experiment into two groups, and then I spent two weeks noticing that one of the groups kept disappearing.
- And once more, with feeling: **software that must fail should fail out loud.** Every hour of this — silent dedupe re-linking, silent chunk replacement, silent list collapse — was spent on the consequences of a thing not saying what it had done.

Rawshuck v1.1.1 marks JPEGs at the very end of the file, where it can't shift anything, and appends in place so nothing about the file's metadata changes either. There's a `--repair` flag for anything marked the old way, and it carries the extended attributes across. And the README now tells you to drag the folder, which is, in retrospect, what I probably should have been doing all along.

If you take one thing from this: when a program does something inexplicable to your files, check whether it's already telling you why. Mine was, for a fortnight, into a log I never opened.

---

**Also needs fixing in the body of the post (unrelated to the addendum):** the paragraph in *The case of the resurrected RAWs* that describes the marking still says the tag is *"a standard JPEG comment segment"* inserted into the file's structure, and calls it a "surgical operation" that only changes "a small text string in the JPEG's `COM` field". That's the v1.0.0 behaviour — the one that turned out to shift the MPF offsets. Suggested replacement for that sentence:

> Rawshuck's commit step offers to *mark* each kept JPEG that's losing its RAW, by appending a tiny tag containing a unique ID to the very end of the file, after all image data. Nothing inside the file moves: the image bitstream is never re-encoded, so the pixels are bit-for-bit identical, EXIF and capture dates are untouched, and the file grows by about fifty bytes. But the checksum changes, so iCloud's dedupe finds no match and your RAWs stay properly, permanently deleted.
