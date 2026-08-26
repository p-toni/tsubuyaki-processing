#!/usr/bin/env python3
"""Reproduce the candidate genotypes used by the hybrid portfolio experiment.

This script does not perform artistic selection. It deterministically regenerates
all hybrid candidates plus the paired D1/B4 baseline candidates from the exact
starting genotypes, mutation code, and RNG seeds used in the experiment.

Run:
    python experiments/hybrid-portfolio-search/reproduce.py

Outputs JSON under experiments/hybrid-portfolio-search/_generated/.
"""
import json
import random
from pathlib import Path

REC_STARTS = {'Rstart1': {'sigma': 9.388341741669965, 'rho': 26.924413646443405, 'beta': 2.0383610592244605, 'dt': 0.0005376901382796321, 'family': 2, 'phase': 0.6571360206334502, 'proj': 'double', 'deform': 'product', 'amp': 0.4523603586493907, 'dz': 15.000027113751754, 'td': 11.999655781756822, 'prod': 54.52034606420026, 'pow': 1.0283020218245933, 'ry': 8.398569047830513, 'side': 4.433214047248926, 'yc': 0.19591189174164236, 'sd': 50.696771002571275, 'tp': 62.48434181830832, 'r0': 48.878158759505396, 'wave': 12.019358500057898, 'wy': 7.018306609794822, 'tw': 13.741790565185546, 'yx': 0.4366391126580367, 'ys': 0.6727605545837317, 'yy': 0.5553365292748838, 'harm': 7.919076189092807, 'harm2': 11.097741175914623, 'scale': 1.6182729167927683, 'alpha': 58, 'samples': 13000}, 'Rstart2': {'sigma': 8.219131987014926, 'rho': 26.822910785034942, 'beta': 1.9313080582343738, 'dt': 0.0004933130169638085, 'family': 2, 'phase': 0.7467677851687217, 'proj': 'fold', 'deform': 'cross', 'amp': 0.25489363090066447, 'dz': 13.997947244934213, 'td': 13.211507344120275, 'prod': 63.625293138882014, 'pow': 0.8613575506496254, 'ry': 9.451610143451507, 'side': 2.4167529594060055, 'yc': 0.115140705416034, 'sd': 55.745855657097934, 'tp': 50.50822600802186, 'r0': 58.498366700188946, 'wave': 11.146817566103682, 'wy': 12.814794723466022, 'tw': 17.902772824533677, 'yx': 0.19813867444000846, 'ys': 0.6739451694296666, 'yy': 0.4736003227448459, 'harm': 6.7377969115906895, 'harm2': 6.442339649044099, 'scale': 1.5080477214526877, 'alpha': 53, 'samples': 13000}, 'Rstart3': {'sigma': 8.778573638038536, 'rho': 27.332150805446087, 'beta': 1.9164881861099061, 'dt': 0.0004962220460438878, 'family': 2, 'phase': 0.6683654745194172, 'proj': 'knot', 'deform': 'product', 'amp': 0.3331001229182893, 'dz': 9.70624680182082, 'td': 11.88882894450504, 'prod': 57.0796085686984, 'pow': 0.7199578231030196, 'ry': 11.40593815334571, 'side': 4.5635843562340135, 'yc': 0.1713468249345527, 'sd': 53.53210145747185, 'tp': 67.06492926822507, 'r0': 66.99246135317323, 'wave': 11.639987074742429, 'wy': 7.077293434718647, 'tw': 13.113963239886498, 'yx': 0.2139140034141172, 'ys': 0.6738573769460237, 'yy': 0.6003913424614701, 'harm': 3.797998956978683, 'harm2': 5.525023731600337, 'scale': 1.6104808594945568, 'alpha': 48, 'samples': 13000}, 'Rstart4': {'sigma': 9.520489328491736, 'rho': 26.043927130744823, 'beta': 1.825131653058482, 'dt': 0.000526282633681377, 'family': 3, 'phase': 0.7167891934362542, 'proj': 'tidal', 'deform': 'recip', 'amp': 0.2438200373584185, 'dz': 15.394072284830624, 'td': 10.742206326447665, 'prod': 44.218015093269955, 'pow': 0.9859451430246485, 'ry': 13.100129649003865, 'side': 4.213248432322821, 'yc': 0.14419117016946575, 'sd': 60.194433252901625, 'tp': 55.36269233845351, 'r0': 56.93270081919559, 'wave': 4.626727850431461, 'wy': 12.914752509730489, 'tw': 16.153280852916193, 'yx': 0.37139945349057846, 'ys': 0.698141831024577, 'yy': 0.3513956492175893, 'harm': 13.914156713681377, 'harm2': 6.152463923921907, 'scale': 1.705252762933454, 'alpha': 52, 'samples': 13000}}
FAM_STARTS = {'Fstart1': {'family': 8, 'phase': 0.5349643807510841, 'layout': 'spiral', 'rx': 88.732653151175, 'ry': 72.15978213389334, 'orbitDrift': 0.05175428361141682, 'orbitT': 39.69247188598089, 'orient': -0.08271429493312332, 'uDiv': 8.2208701969461, 'sx': 15.282807038418943, 'sy': 9.75299810903237, 'f1': 3, 'f2': 7, 'f3': 3, 'mix': 3.1005536705722347, 'mix2': 5.971464724160418, 'norm': 11.46766585726104, 'deform': 'recip', 'amp': 0.547632690083391, 'df': 4.143821664756317, 'td': 17.37117524499346, 'pow': 0.7107303576082156, 'twist': 0.19820403670628942, 'twf': 2.3547255140502275, 'ta': 60.368696153845114, 'shape': 'lens', 'bx': 7.797753957940985, 'by': 6.207760539322028, 'kx': 0.8440745600971236, 'ey': 0.7942554809299692, 'tri': 5.196351712344101, 'alpha': 55, 'samplesBody': 1700}, 'Fstart2': {'family': 6, 'phase': 0.8415801910005125, 'layout': 'spiral', 'rx': 102.82266211798088, 'ry': 58.402746950282264, 'orbitDrift': 0.08473472114056416, 'orbitT': 27.834140684442772, 'orient': 0.20658567940863604, 'uDiv': 9.538183786730535, 'sx': 10.079505748052028, 'sy': 8.720692881016799, 'f1': 2, 'f2': 6, 'f3': 3, 'mix': 2.8174375023922336, 'mix2': 7.748978854346539, 'norm': 17.19059850732035, 'deform': 'pulse', 'amp': 0.5123283996457818, 'df': 2.6645174508003318, 'td': 11.587118775501546, 'pow': 1.0651371602896498, 'twist': 0.2577061359549434, 'twf': 2.2950856665739283, 'ta': 53.91674128832316, 'shape': 'shell', 'bx': 9.201493632140174, 'by': 6.472961700727779, 'kx': 0.6338504890177866, 'ey': 0.6275396956102021, 'tri': 3.185791272295101, 'alpha': 43, 'samplesBody': 1700}, 'Fstart3': {'family': 6, 'phase': 0.945132968683418, 'layout': 'ring', 'rx': 101.10414573037214, 'ry': 76.81798884905326, 'orbitDrift': 0.03524263024986197, 'orbitT': 35.306557452622854, 'orient': -0.039324514367860275, 'uDiv': 12.520324549270217, 'sx': 8.795005041868844, 'sy': 9.66694660323702, 'f1': 4, 'f2': 5, 'f3': 5, 'mix': 3.022941513993506, 'mix2': 4.300712451469551, 'norm': 17.404197990725752, 'deform': 'pulse', 'amp': 0.5261690988547367, 'df': 2.9322545748311395, 'td': 21.663023562533173, 'pow': 0.8553929551327624, 'twist': 0.16182614046109683, 'twf': 2.1833155588432778, 'ta': 36.76605585148414, 'shape': 'shell', 'bx': 9.05247074033284, 'by': 11.101100498797084, 'kx': 0.7395037635944237, 'ey': 0.6338614375583007, 'tri': 1.4374582906442581, 'alpha': 56, 'samplesBody': 1700}, 'Fstart4': {'family': 7, 'phase': 0.863842918370231, 'layout': 'spiral', 'rx': 94.89180220997028, 'ry': 66.50431853442387, 'orbitDrift': 0.08839628393122392, 'orbitT': 49.87386163138727, 'orient': -0.3848291501887124, 'uDiv': 8.306072387629264, 'sx': 7.89152669735409, 'sy': 15.376822217945744, 'f1': 5, 'f2': 3, 'f3': 5, 'mix': 2.7719529227720687, 'mix2': 5.287391807988522, 'norm': 14.324472191766606, 'deform': 'power', 'amp': 0.5222498667383207, 'df': 1.902707822800955, 'td': 11.396619437496582, 'pow': 0.7569002742441384, 'twist': 0.30272814459151326, 'twf': 3.3286009392205287, 'ta': 52.401833496087775, 'shape': 'seed', 'bx': 5.896184358702699, 'by': 8.213951893371199, 'kx': 0.5378473135968894, 'ey': 0.859827246796204, 'tri': 3.3184565578371448, 'alpha': 52, 'samplesBody': 1700}}


def mutate_rec(base, rng):
    g = dict(base)
    roles = rng.sample([
        "kernel","dt","family","phase","projection","deform","amp",
        "projection_constants","time","harmonics","scale"
    ], rng.randint(4,7))
    if "kernel" in roles:
        g["sigma"] = base["sigma"] * rng.uniform(.90,1.10)
        g["rho"] = base["rho"] * rng.uniform(.94,1.06)
        g["beta"] = base["beta"] * rng.uniform(.88,1.12)
    if "dt" in roles: g["dt"] = base["dt"] * rng.uniform(.90,1.10)
    if "family" in roles: g["family"] = rng.choice([1,2,2,3,4])
    if "phase" in roles: g["phase"] = base["phase"] * rng.uniform(.76,1.28)
    if "projection" in roles and rng.random() < .55:
        g["proj"] = rng.choice(["tidal","fold","double","knot"])
    if "deform" in roles and rng.random() < .65:
        g["deform"] = rng.choice(["cross","product","pulse","recip","shear"])
    if "amp" in roles:
        g["amp"] = max(.12, min(.65, base["amp"] * rng.uniform(.68,1.42)))
    if "projection_constants" in roles:
        for k,lo,hi in [("yc",.08,.45),("sd",42,76),("r0",40,78),("wave",2,17),
                        ("yx",.08,.6),("ys",.4,.82),("yy",.03,.8)]:
            g[k] = max(lo, min(hi, base[k] * rng.uniform(.82,1.18)))
    if "time" in roles:
        g["tp"] = max(28, min(110, base["tp"] * rng.uniform(.75,1.3)))
        g["td"] = max(5, min(20, base["td"] * rng.uniform(.75,1.3)))
        g["tw"] = max(5, min(24, base["tw"] * rng.uniform(.75,1.3)))
    if "harmonics" in roles:
        g["harm"] = max(0, min(20, base["harm"] * rng.uniform(.55,1.55)))
        g["harm2"] = max(0, min(18, base["harm2"] * rng.uniform(.55,1.55)))
        g["wy"] = max(5, min(16, base["wy"] * rng.uniform(.75,1.3)))
    if "scale" in roles:
        g["scale"] = max(.95, min(1.9, base["scale"] * rng.uniform(.88,1.12)))
    return g, roles


def mutate_fam(base, rng):
    g = dict(base)
    roles = rng.sample([
        "family","phase","layout","orbit","harmonics","latent","deform","shape","time","material"
    ], rng.randint(4,7))
    if "family" in roles: g["family"] = rng.choice([5,6,7,8,9,10,11])
    if "phase" in roles: g["phase"] = max(.25, min(1.35, base["phase"] * rng.uniform(.72,1.35)))
    if "layout" in roles and rng.random() < .35:
        g["layout"] = rng.choice(["ring","arc","spiral","drift"])
    if "orbit" in roles:
        g["rx"] = max(50, min(115, base["rx"] * rng.uniform(.82,1.18)))
        g["ry"] = max(42, min(100, base["ry"] * rng.uniform(.82,1.18)))
        g["orbitDrift"] = max(0, min(.16, base["orbitDrift"] * rng.uniform(.55,1.6)))
        g["orient"] = base["orient"] + rng.uniform(-.25,.25)
    if "harmonics" in roles:
        g["f1"] = rng.choice([2,3,4,5,6]); g["f2"] = rng.choice([3,4,5,6,7,8]); g["f3"] = rng.choice([2,3,4,5,6])
        g["mix"] = max(1.3, min(4.8, base["mix"] * rng.uniform(.75,1.3)))
        g["mix2"] = max(3, min(11, base["mix2"] * rng.uniform(.75,1.3)))
    if "latent" in roles:
        g["sx"] = max(4, min(21, base["sx"] * rng.uniform(.72,1.35)))
        g["sy"] = max(5, min(23, base["sy"] * rng.uniform(.72,1.35)))
        g["uDiv"] = max(3.5, min(18, base["uDiv"] * rng.uniform(.72,1.35)))
    if "deform" in roles:
        if rng.random() < .55: g["deform"] = rng.choice(["pulse","wave","recip","power"])
        g["amp"] = max(.12, min(.75, base["amp"] * rng.uniform(.62,1.45)))
        g["df"] = max(1, min(5.5, base["df"] * rng.uniform(.7,1.35)))
        g["pow"] = max(.4, min(1.5, base["pow"] * rng.uniform(.75,1.3)))
    if "shape" in roles:
        if rng.random() < .45: g["shape"] = rng.choice(["seed","lens","tri","shell"])
        g["bx"] = max(2, min(14, base["bx"] * rng.uniform(.72,1.3)))
        g["by"] = max(3, min(18, base["by"] * rng.uniform(.72,1.3)))
        g["kx"] = max(.25, min(1.2, base["kx"] * rng.uniform(.7,1.35)))
        g["ey"] = max(.3, min(1.25, base["ey"] * rng.uniform(.7,1.35)))
        g["tri"] = max(0, min(9, base["tri"] * rng.uniform(.55,1.5)))
    if "time" in roles:
        g["orbitT"] = max(12, min(90, base["orbitT"] * rng.uniform(.7,1.4)))
        g["td"] = max(5, min(30, base["td"] * rng.uniform(.7,1.4)))
        g["ta"] = max(14, min(110, base["ta"] * rng.uniform(.7,1.4)))
    if "material" in roles:
        g["alpha"] = max(32, min(72, int(base["alpha"] * rng.uniform(.78,1.25))))
        g["samplesBody"] = max(1100, min(2300, int(base["samplesBody"] * rng.uniform(.82,1.2))))
    return g, roles


def make_round(mutator, base, prefix, count, seed):
    rng = random.Random(seed)
    return [{"id": f"{prefix}-{i+1}", "g": mutator(base,rng)[0]} for i in range(count)]


def generate_recurrence():
    rng = random.Random(26082671)
    exploration = {}
    for s in range(1,5):
        base = REC_STARTS[f"Rstart{s}"]
        exploration[str(s)] = []
        for j in range(5):
            g,roles = mutate_rec(base,rng)
            exploration[str(s)].append({"id":f"RE-S{s}-{j+1}","g":g,"roles":roles})
    e1 = exploration["1"][4]["g"]
    e2 = exploration["3"][2]["g"]
    h1r1 = make_round(mutate_rec,e1,"RH1-R1",10,26082672)
    h1r2 = make_round(mutate_rec,h1r1[0]["g"],"RH1-R2",10,26082673)
    h2a = make_round(mutate_rec,e1,"RH2-B1",10,26082674)
    h2b = make_round(mutate_rec,e2,"RH2-B3",10,26082675)
    d1r1 = make_round(mutate_rec,REC_STARTS["Rstart1"],"RDP-R1",10,26082701)
    d1r2 = make_round(mutate_rec,d1r1[5]["g"],"RDP-R2",10,26082702)
    d1r3 = make_round(mutate_rec,d1r2[1]["g"],"RDP-R3",10,26082703)
    d1r4 = make_round(mutate_rec,d1r2[1]["g"],"RDP-R4",10,26082704)
    rngb = random.Random(26082710)
    b4={}
    for s in range(1,5):
        base=REC_STARTS[f"Rstart{s}"]; b4[str(s)]=[]
        for j in range(10):
            g,roles=mutate_rec(base,rngb)
            b4[str(s)].append({"id":f"RBP-S{s}-{j+1}","g":g,"roles":roles})
    return {"starts":REC_STARTS,"exploration":exploration,"H1":{"round1":h1r1,"round2":h1r2},"H2":{"basin1":h2a,"basin3":h2b},"pairedD1":{"round1":d1r1,"round2":d1r2,"round3":d1r3,"round4":d1r4},"pairedB4":b4,"selection":{"explorationBasinOrder":[1,3,4,2],"H1Winner":"RH1-R2-3","H2Winner":"RH2-B1-2","pairedD1Winner":"RDP-R2-2","pairedB4Winner":"RBP-S1-3"}}


def generate_family():
    rng = random.Random(26082681)
    exploration={}
    for s in range(1,5):
        base=FAM_STARTS[f"Fstart{s}"]; exploration[str(s)]=[]
        for j in range(5):
            g,roles=mutate_fam(base,rng)
            exploration[str(s)].append({"id":f"FE-S{s}-{j+1}","g":g,"roles":roles})
    e1=exploration["4"][0]["g"]; e2=exploration["1"][2]["g"]
    h1r1=make_round(mutate_fam,e1,"FH1-R1",10,26082682)
    h1r2=make_round(mutate_fam,h1r1[1]["g"],"FH1-R2",10,26082683)
    h2a=make_round(mutate_fam,e1,"FH2-B4",10,26082684)
    h2b=make_round(mutate_fam,e2,"FH2-B1",10,26082685)
    d1r1=make_round(mutate_fam,FAM_STARTS["Fstart1"],"FDP-R1",10,26082721)
    d1r2=make_round(mutate_fam,d1r1[7]["g"],"FDP-R2",10,26082722)
    d1r3=make_round(mutate_fam,d1r2[7]["g"],"FDP-R3",10,26082723)
    d1r4=make_round(mutate_fam,d1r3[5]["g"],"FDP-R4",10,26082724)
    rngb=random.Random(26082730); b4={}
    for s in range(1,5):
        base=FAM_STARTS[f"Fstart{s}"]; b4[str(s)]=[]
        for j in range(10):
            g,roles=mutate_fam(base,rngb)
            b4[str(s)].append({"id":f"FBP-S{s}-{j+1}","g":g,"roles":roles})
    return {"starts":FAM_STARTS,"exploration":exploration,"H1":{"round1":h1r1,"round2":h1r2},"H2":{"basin4":h2a,"basin1":h2b},"pairedD1":{"round1":d1r1,"round2":d1r2,"round3":d1r3,"round4":d1r4},"pairedB4":b4,"selection":{"explorationBasinOrder":[4,1,3,2],"H1Winner":"FH1-R2-6","H2Winner":"FH2-B4-4","pairedD1Winner":"FDP-R3-6","pairedB4Winner":"FBP-S1-8"}}


def main():
    out=Path(__file__).with_name("_generated")
    out.mkdir(exist_ok=True)
    (out/"recurrence-candidates.json").write_text(json.dumps(generate_recurrence(),indent=2)+"\n")
    (out/"family-candidates.json").write_text(json.dumps(generate_family(),indent=2)+"\n")
    print(out)

if __name__ == "__main__": main()
