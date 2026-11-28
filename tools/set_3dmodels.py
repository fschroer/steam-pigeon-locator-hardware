"""Point every footprint's 3D model at the project-local lib/3dmodels folder.

Updates RocketLocator.kicad_pcb and lib/Custom.pretty in place (text edit, so
KiCad does not rewrite the project file). Run from the repo root.
"""
import re, glob, os

P = "${KIPRJMOD}/lib/3dmodels/"
K = P + "kicad/"
# footprint lib_id -> (model path, rotate z)
MAP = {
    "Resistor_SMD:R_0402_1005Metric": (K + "R_0402_1005Metric.step", 0),
    "Capacitor_SMD:C_0402_1005Metric": (K + "C_0402_1005Metric.step", 0),
    "Capacitor_SMD:C_1206_3216Metric": (K + "C_1206_3216Metric.step", 0),
    "LED_SMD:LED_0402_1005Metric": (K + "LED_0402_1005Metric.step", 0),
    "Package_LGA:LGA-8_3x5mm_P1.25mm": (K + "LGA-8_3x5mm_P1.25mm.step", 0),
    "Package_LGA:LGA-16_3x3mm_P0.5mm": (K + "LGA-16_3x3mm_P0.5mm.step", 0),
    "Package_DFN_QFN:Diodes_UDFN2020-6_Type-F": (P + "Diodes_UDFN2020-6_Type-F.step", 0),
    "Custom:JEITA_SOIC-8_3.9x4.9mm_P1.27mm": (K + "JEITA_SOIC-8_3.9x4.9mm_P1.27mm.step", 0),
    "Custom:PinHeader_1x04_P2.54mm_Vertical": (K + "PinHeader_1x04_P2.54mm_Vertical.step", 0),
    "Custom:PinHeader_1x06_P2.54mm_Vertical_Pos4-5_Empty": (K + "PinHeader_1x06_P2.54mm_Vertical.step", 0),
    "Custom:SOT94P280X100-5N": (K + "SOT-23-5.step", 0),
    "Custom:SOP-8_5.28x5.23mm_P1.27mm": (K + "SOIC-8_5.3x5.3mm_P1.27mm.step", 0),
    "Custom:HRS_U.FL-R-SMT(01)": (K + "U.FL_Hirose_U.FL-R-SMT-1_Vertical.step", 90),
    "Custom:BQ25185DLHR": (K + "Texas_DLH0010A_WSON-10-1EP_2.2x2mm_P0.4mm_EP0.9x1.5mm.step", 0),
    "Custom:U_LGA-14L_2p5X3p0X0p83_STM": (K + "LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y.step", 0),
    "Custom:W-QFN2020-12-EP(2x2)": (K + "UQFN-12-1EP_2x2mm_P0.4mm_EP1.1x1.1mm.step", 0),
    "Custom:SAMTEC_FTR-107-51-G-D": (K + "PinHeader_2x07_P1.27mm_Vertical_SMD.step", 90),
    "Custom:LED_XL-Z1912RGBA-SG": (P + "LED_XL-Z1912RGBA-SG.step", 0),
    "Custom:IC_TPS22950YBHR": (P + "Texas_DSBGA-6_YBH_0.8x1.2mm_P0.4mm.step", 0),
    "Custom:X2SON": (P + "TI_X2SON-4-1EP_1.1x1.4mm.step", 0),
    "Custom:Nexperia_DFN1010D-3_SOT1215": (P + "Nexperia_DFN1010D-3_SOT1215.step", 0),
    "Custom:DFN1006-3L": (P + "DFN1006-3L_1.0x0.6mm.step", 0),
    "Custom:WQFN 14 3.00 mm × 2.50 mm": (P + "Texas_BQA_WQFN-14-1EP_2.5x3mm_P0.5mm.step", 0),
    "Custom:LGA-92_10X10_STM": (P + "ST_LGA-92_10x10mm_STM32WL5MOC.step", 0),
    "Custom:XCVR_SAM-M10Q-00B": (P + "u-blox_SAM-M10Q.step", 0),
    "Custom:PiezoBuzzer": (P + "Buzzer_Piezo_D14mm_H7mm_RM7.6.step", 0),
    "Custom:USB_C_Receptacle_Palconn_UTC16-G": (P + "USB_C_Receptacle_Palconn_UTC16-G.step", 0),
    "Capacitor_SMD:C_0201_0603Metric": (K + "C_0201_0603Metric.step", 0),
    "Inductor_SMD:L_0201_0603Metric": (K + "L_0201_0603Metric.step", 0),
    "Inductor_SMD:L_0402_1005Metric": (K + "L_0402_1005Metric.step", 0),
    "Inductor_SMD:L_0603_1608Metric": (K + "L_0603_1608Metric.step", 0),
    "Inductor_SMD:L_0805_2012Metric": (K + "L_0805_2012Metric.step", 0),
    "Crystal:Crystal_SMD_2016-4Pin_2.0x1.6mm": (K + "Crystal_SMD_2016-4Pin_2.0x1.6mm.step", 0),
    # stand-ins: no stock model for these footprints; same body outline
    "Crystal:Crystal_SMD_2012-2Pin_2.0x1.2mm": (K + "Crystal_SMD_2016-4Pin_2.0x1.6mm.step", 0),
    "Oscillator:Oscillator_SMD_SiT_PQFN-4Pin_2.0x1.6mm": (K + "Crystal_SMD_2016-4Pin_2.0x1.6mm.step", 0),
    "Package_DFN_QFN:QFN-48-1EP_6x6mm_P0.4mm_EP4.6x4.6mm": (K + "UQFN-48-1EP_6x6mm_P0.4mm_EP4.45x4.45mm.step", 0),
    "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm": (K + "QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm.step", 0),
    "Package_SO:TSSOP-16_4.4x5mm_P0.65mm": (K + "TSSOP-16_4.4x5mm_P0.65mm.step", 0),
    "Package_TO_SOT_SMD:SOT-363_SC-70-6": (K + "SOT-363_SC-70-6.step", 0),
    "RF_Antenna:Johanson_2450AT18x100": (K + "Johanson_2450AT18x100.step", 0),
}

MODEL_RE = re.compile(r'\r?\n(\t+)\(model "[^"]*"\r?\n.*?\r?\n\1\)', re.S)


def model_block(ind, path, rz, nl):
    i = ind
    lines = [f'{i}(model "{path}"', f'{i}\t(offset', f'{i}\t\t(xyz 0 0 0)', f'{i}\t)',
             f'{i}\t(scale', f'{i}\t\t(xyz 1 1 1)', f'{i}\t)', f'{i}\t(rotate', f'{i}\t\t(xyz 0 0 {rz})',
             f'{i}\t)', f'{i})']
    return nl + nl.join(lines)


def fix(fp, lib_id, ind, nl):
    """fp: one footprint's text, ending with its closing paren. ind: child indent."""
    if lib_id not in MAP:
        return fp
    path, rz = MAP[lib_id]
    fp = MODEL_RE.sub("", fp)
    k = fp.rfind(")")                      # footprint's own closing paren
    head = fp[:k].rstrip("\r\n\t ")       # ends with the last child's ")"
    tail_ws = fp[len(head):k]             # newline + indent before closing paren
    return head + model_block(ind, path, rz, nl) + tail_ws + fp[k:]


# --- board ---
pcb = "RocketLocator.kicad_pcb"
t = open(pcb, encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in t else "\n"
starts = [m.start() for m in re.finditer(r'\n\t\(footprint "', t)]
out, last, n = [], 0, 0
for s in starts:
    e = t.index(nl + "\t)", s + 1) + len(nl) + 2
    blk = t[s:e]
    lib_id = re.match(r'\n\t\(footprint "([^"]+)"', blk).group(1)
    new = fix(blk, lib_id, "\t\t", nl)
    n += new != blk
    out.append(t[last:s]); out.append(new); last = e
out.append(t[last:])
open(pcb, "w", encoding="utf-8", newline="").write("".join(out))
print("board footprints changed:", n, "of", len(starts))

# --- library ---
for f in sorted(glob.glob("lib/Custom.pretty/*.kicad_mod")):
    lib_id = "Custom:" + os.path.basename(f)[:-10]
    t = open(f, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in t else "\n"
    body = t.rstrip("\r\n")
    new = fix(body, lib_id, "\t", nl) + t[len(body):]
    if new != t:
        open(f, "w", encoding="utf-8", newline="").write(new)
        print("lib:", os.path.basename(f))
