"""Convert TeX Gyre Termes (GUST Font License) OTF/CFF to TrueType so matplotlib
can embed it as Type 42 without CFF-in-TrueType mismatches."""
import glob, os
from fontTools.ttLib import TTFont, newTable
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

out = os.path.join(os.path.dirname(__file__), "fonts")
for src in glob.glob("/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyretermes-*.otf"):
    f = TTFont(src)
    gs = f.getGlyphSet()
    glyf = newTable("glyf"); glyf.glyphs = {}; glyf.glyphOrder = f.getGlyphOrder()
    for name in f.getGlyphOrder():
        pen = TTGlyphPen(gs)
        gs[name].draw(Cu2QuPen(pen, max_err=1.0, reverse_direction=True))
        glyf[name] = pen.glyph()
    f["glyf"] = glyf
    f["loca"] = newTable("loca")
    del f["CFF "]
    if "VORG" in f: del f["VORG"]
    f["maxp"].tableVersion = 0x00010000
    for a in ("maxZones", "maxTwilightPoints", "maxStorage", "maxFunctionDefs", "maxInstructionDefs",
              "maxStackElements", "maxSizeOfInstructions", "maxComponentElements",
              "maxPoints", "maxContours", "maxCompositePoints", "maxCompositeContours", "maxComponentDepth"):
        setattr(f["maxp"], a, 0)
    f["maxp"].maxZones = 2
    f["head"].indexToLocFormat = 0; f["head"].glyphDataFormat = 0
    f["post"].formatType = 2.0; f["post"].extraNames = []; f["post"].mapping = {}
    f.sfntVersion = "\x00\x01\x00\x00"
    f.save(os.path.join(out, os.path.basename(src).replace(".otf", ".ttf")))
    print("wrote", os.path.basename(src))
