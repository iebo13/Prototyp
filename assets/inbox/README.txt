ASSETS INBOX — what to drop here and why
=========================================

Neither OPENAI_API_KEY nor GEMINI_API_KEY was set in the build environment, so no
image-model generation ran. Every asset that would have been generated was built
another way (hand-authored vector, or a procedural vector background) and is marked
PLACEHOLDER in AV-Brand-Kit/README.md.

To upgrade any of them: generate the image with the exact prompt below, drop the file
into this folder under the given filename, and tell Claude Code
"I added assets/inbox/<filename>, rebuild". Nothing else needs changing.

None of these prompts contain the logo. The logo is never generated, redrawn or
restyled by an image model — it is always the real vector, composited on top.

-------------------------------------------------------------------------------
P1  ->  feather.png          (GPT Image 2, transparent background, largest square)
        Replaces: the hand-authored assets/feather.svg
        Command:  python3 scripts/gen_gpt_image.py --prompt-file assets/inbox/P1_feather.txt --out assets/feather.png
        Fallback: nano-banana "<P1>" -t -s 2K -o feather -d assets

Single peacock feather, flat vector illustration, exactly four flat colours: green
#337B56, teal #21897F, gold #D1A976, dark green #062014. No gradients, no texture, no
shading, hard clean edges. The feather curves gently up to the right like a
calligraphic stroke, thin gold spine, one eye near the top. Isolated object, nothing
else in frame.

-------------------------------------------------------------------------------
P2  ->  bg_square.png (1:1) and bg_wide.png (16:9)     (Nano Banana 2, 4K)
        Replaces: the procedural backgrounds behind the Instagram post and OG image

Subtle dark forest green textured paper background, colour #062014, faint fine
hairline mountain silhouette in gold #D1A976 in the bottom-right corner, large empty
calm area, premium minimal aesthetic, no text, no logo, no watermark, no people.

-------------------------------------------------------------------------------
P3  ->  bg_story.png (9:16)                            (Nano Banana 2, 4K)
        Replaces: the procedural Instagram Story background

Subtle dark forest green textured paper background, colour #062014, faint fine
hairline mountain silhouette along the bottom edge in gold #D1A976, empty upper two
thirds, premium minimal aesthetic, no text, no logo, no watermark, no people.

-------------------------------------------------------------------------------
P4  ->  hero.png (21:9, 4K)                            (Nano Banana 2)
        Replaces: the procedural 06_Web/hero_1920x800.jpg
        NOTE: {{region_for_hero}} is still an unfilled placeholder in CLAUDE.md.
              Fill it in before generating, or the model picks a random region.

Editorial real-estate photograph, elegant modern villa exterior at golden hour in
{{region_for_hero}}, deep green pines, soft haze on distant peaks, warm cream and gold
light, muted luxury colour grade in forest green #062014, cream #EBE1CC and gold
#D1A976. Wide composition with the left third empty and calm for text overlay. No
people, no text, no logos, no watermarks, ultra sharp.

-------------------------------------------------------------------------------
P5  ->  expose_cover.png (3:4, 4K)                     (Nano Banana 2)
        Replaces: the procedural background on 04_Print/Expose_Cover_A4

Bright architectural interior photograph, high-ceilinged living room with large
windows, warm daylight, neutral cream and oak tones with deep green accents, empty
upper third for a title, no text, no people, no watermarks, editorial magazine quality.

-------------------------------------------------------------------------------
P6  ->  slide_texture.png (16:9)                       (Nano Banana 2)
        Optional. Texture for the PowerPoint content master.

Very subtle cream paper texture #EBE1CC, almost plain, faint gold hairline rule at the
bottom, nothing else, no text, no logo.

-------------------------------------------------------------------------------
P7  ->  review/mockups/  (presentation only, NEVER a deliverable)
        Requires nano-banana -r with a real exported PNG as the reference image.

Photorealistic product mockup of a {{item}}, dark green #062014 material with the
attached logo in gold foil, applied exactly as given — do not redraw, alter or restyle
the logo. Soft studio light, shallow depth of field, 3:2.

Suggested items: business card, office door sign, Verkaufsschild on a lawn,
letterhead on a desk.
