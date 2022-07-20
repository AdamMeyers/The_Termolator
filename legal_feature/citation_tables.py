## Sources:  https://lib.law.washington.edu/ref/repdig.html  
## https://en.wikipedia.org/wiki/National_Reporter_System
## https://www.fcsl.edu/ltc/index.php?q=resources/research_guides/bluebook_abbrev
## http://lawlibguides.valpo.edu/content.php?pid=473684&sid=3926154

## allow variations in which spaces are eliminated from abbreviations
## and variations in which they are added after periods
## but regularize to one entry (with/without space ?)

import re
from reporters_db import REPORTERS ## this only seems to work (so far) for Python 3.5 and higher

## REPORTERS is a dictionary
## The keys are reporters
## The values are lists of dictionaries, usually just one list, but occasionally 2
## We will assume for now that if there are 2 entries, the first is correct
## -- this only effects 9 instances
## -- in fact there is some other detail (under variations) which can help disambiguate
##
## the keys in the dictionaries include the following:
## 'mlz_jurisdiction', 'cite_type', 'publisher', 'editions', 'variations', 'href', 'name', 'notes'
## -- jurisdiction and name?
## cit_type includes the following possibilities:
## see bottom of file for details

court_reporter_abbreviation_table = {}
court_reporter_standard_table = {}

court_reporter_rexp_list = []
court_reporter_rexp = ''

def regexp_friendly_variant(instring):
        instring = re.sub(' ',' *',instring)
        instring = re.sub('\.','\.',instring)
        return(instring)

def get_abbrev_variation(instring):
        variant1 = re.sub('\. +','.',instring)
        variant2 = re.sub('\.','. ',variant1)
        variant2 = variant2.rstrip(' ') ## don't put spaces after final .
        trailing_Nd_pattern=re.compile('\.([0-9]+d)$')
        match = trailing_Nd_pattern.search(variant1)
        if match:
                variant3 = variant1[0:match.start(1)]+' '+variant1[match.start(1):]
        else:
                variant3 = False
        if "." in instring:
	        variant4 = re.sub('\. ?',' ',instring).strip(" ")
        else:
                variant4 = False
        ## assume variant1 (no spaces after .) is the standard
        ## variant2 has one space after each period
        return([variant1,variant2,variant3,variant4])

for triple in [
	## given two entries such that X is a prefix of Y, Y must always be listed before X
        ["A. 2d","CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT","Atlantic Reporter, 2d series"],
        ["A. 3d","CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT","Atlantic Reporter, 3d series"],
        ["A.","CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT","Atlantic Reporter"],
        ["B. R.","Bankruptcy Courts","West's Bankruptcy Reporter"],
        ["Cal. Rptr. 2d","Supreme Court of California","California Reporter, 2d series"],
        ["Cal. Rptr. 3d","Supreme Court of California","California Reporter, 3d series"],
        ["Cal. Rptr.","Supreme Court of California","California Reporter"],
        ["Ct. Int'l Trade","United States Court of International Trade Reports","Court of International Trade"],
        ["F. Supp. 2d","District Courts","West's Federal Supplement, 2d Series"],
        ["F. Supp. 3d","District Courts","West's Federal Supplement, 3d Series"],
        ["F. Supp.","District Courts","Federal Supplement"],
        ["F. 2d","Courts of Appeal","Federal Reporter, 2d Series"],
        ["F. 3d","Courts of Appeal","West's Federal Reporter, 3d Series"],
        ["F. Cas.","District Courts","Federal Cases"],
        ["F. R. D.","District Courts","Federal Rules Decisions"],
        ["F.","Courts of Appeal","Federal Reporter"],
        ["Fed. Cl.","Federal Claims Reporter","Court of Claims"],
        ["Fed. Appx.","Courts of Appeal","Federal Appendix"],
        ["L. Ed. 2d","Supreme Court","United States Supreme Court Reports, Lawyers' Edition 2"],
        ["L. Ed.","Supreme Court","United States Supreme Court Reports, Lawyers' Edition 1"],
        ["M. J.","West's Military Justice Reporter","Court of Appeals for the Armed Forces"],
        ["N. E. 2d","IL, IN, MA, NY, OH","North Eastern Reporter, 2d series"],
        ["N. E.","IL, IN, MA, NY, OH","North Eastern Reporter"],
        ["N. W. 2d","IA, MI, MN, NE, ND, SD, WI","North Western Reporter, 2d series"],
        ["N. W.","IA, MI, MN, NE, ND, SD, WI","North Western Reporter"],
        ["N. Y. S. 2d","NY","New York Supplement, 2d series"],
        ["N. Y. S.","NY","New York Supplement"],
        ["P. 2d","AK, AZ, CA, CO, HI, ID, KS, MT, NV, NM, OK, OR, UT, WA, WY","Pacific Reporter, 2d series"],
        ["P. 3d","AK, AZ, CA, CO, HI, ID, KS, MT, NV, NM, OK, OR, UT, WA, WY","Pacific Reporter, 3d series"],
        ["P.","AK, AZ, CA, CO, HI, ID, KS, MT, NV, NM, OK, OR, UT, WA, WY","Pacific Reporter"],
        ["S. Ct.","Supreme Court","Supreme Court Reporter"],
        ["S. E. 2d","GA, NC, SC, VA, WV","South Eastern Reporter, 2d series"],
        ["S. E.","GA, NC, SC, VA, WV","South Eastern Reporter"],
        ["S. W. 2d","AR, KY, MO, TN, TX","South Western Reporter, 2d series"],
        ["S. W. 3d","AR, KY, MO, TN, TX","South Western Reporter, 3d series"],
        ["S. W.","AR, KY, MO, TN, TX","South Western Reporter"],
        ["So. 2d","AL, FL, LA, MS","Southern Reporter, 2d series"],
        ["So. 3d","AL, FL, LA, MS","Southern Reporter, 3d series"],
        ["So.","AL, FL, LA, MS","Southern Reporter"],
        ["T. C.","United States Tax Court Reports","Tax Court"],
        ["U. S.","Supreme Court","United States Reports"],
        ["Vet. App.","Court of Appeals for Veterans Claims","West's Veterans Appeals Reporter"],
        ["Wash. 2d","Washington Supreme Court","Washington Reports, 2d"],
        ["Wash. App.","Washington Court of Appeals","Washington Appellate Reports"],
        ["Wash.","Washington Supreme Court","Washington Reports"],
        ["Wn. 2d","Washington Supreme Court","Washington Reports, 2d"],
        ["Wn. App.","Washington Court of Appeals","Washington Appellate Reports"]]:
        variants =get_abbrev_variation(triple[0])
        standard = variants[0]
        for variant in variants:
                if variant:
                    v = regexp_friendly_variant(variant)
                    if not v in court_reporter_rexp_list:
                        court_reporter_rexp_list.append(v)
                        ## court_reporter_rexp=court_reporter_rexp+'|'
                        ## court_reporter_rexp = court_reporter_rexp+regexp_friendly_variant(variant)
	## get rid of intial | so the disjunction doesn't match the empty string
        result=[standard]
        result.extend(triple[1:])
        for variant in variants:
                if variant:
                        court_reporter_abbreviation_table[variant.upper()]=result
                        court_reporter_standard_table[variant.upper()]=standard.upper()



for abbrev,variant,full,year_in,year_out in [['Dall','Dallas','Dallas','1790','1800'], 
					     ['Cranch','','Cranch','1801','1815'],
					     ['Wheat','Wheat.','Wheaton','1816','1827'],
					     ['Pet','Pet.','Peters','1828','1842'],
					     ['How','How.','Howard','1843','1860'],
					     ['Black','','Black','1861','1862'],
					     ['Wall','Wall.','Wallace','1863','1874']]:
	if variant != '':
		v = regexp_friendly_variant(variant)
		if not v in court_reporter_rexp_list:
		    court_reporter_rexp_list.append(v)
		## court_reporter_abbreviation_table[variant.upper()]=abbrev.upper()
		## court_reporter_rexp=court_reporter_rexp+'|'+regexp_friendly_variant(variant)
	court_reporter_abbreviation_table[abbrev.upper()]=abbrev.upper()
	v = regexp_friendly_variant(abbrev)
	if not v in court_reporter_rexp_list:
	    court_reporter_rexp_list.append(v)
	### court_reporter_rexp=court_reporter_rexp+'|'+regexp_friendly_variant(abbrev)
	### These are the early United States Reports court reporters (for the Supreme Court) along with
	### their terms (year_in, year_out)

## court_reporter_rexp=court_reporter_rexp[1:]
## trim off initial vertical bar

## more tables?
## http://www.courts.wa.gov/appellate_trial_courts/supreme/?fa=atc_supreme.style


State_court_abbreviations = [["Ala.", "Alabama Supreme Court"],
			     ["Ala. Civ. App.","Alabama Court of Civil Appeals"],
			     ["Ala. Crim. App.","Alabama Court of Criminal Appeals"],
			     ["Alaska","Alaska Supreme Cout"],
			     ["Alaska Ct. App.","Alaska Court of Appeals"],
			     ["Ariz.","Arizona Surpreme Courts"],
			     ["Ariz. Ct. App. ","Arizona Court of Appeals"],
			     ["Ark.","Arkansas Supreme Court"],
			     ["Ark. Ct. App.","Arkansas Court of Appeals"],
			     ["Cal.","California Supreme Court"],
			     ["Cal. Ct. App.","California Court of Appeal"],
			     ["Colo.","Colorado Supreme Court"],
			     ["Colo. App.","Colorado Court of Appeals"],
			     ["Conn.","Connecticut Supreme Court"],
			     ["Conn. App. Ct.","Connecticut Appellate Court"],
			     ["Del.","Delaware Supreme Court"],
			     ["Del. Ch.","Delaware Court of Chancery"],
			     ["D.C.","District of Columbia Court of Appeals"],
			     ["Fla.","Florida Supreme Court"],
			     ["Fla. Dist. Ct. App.","Florida District Court of Appeal"],
			     ["Ga.","Georgia Supreme Court"],
			     ["Ga. Ct. App.","Georgia Court of Appeals"],
			     ["Haw.","Hawaii Supreme Court"],
			     ["Haw. St. App.","Hawaii Court of Appeals"],
			     ["Idaho","Idaho Supreme Court"],
			     ["Idaho Ct. App.","Idaho Court of Appeals"],
			     ["Ill.","Illinois Supreme Court"],
			     ["Ill. App. Ct.","Illinois Appellate Court"],
			     ["Ind.","Indiana Supreme Court"],
			     ["Ind. Ct. App.","Indiana Court of Appeals"],
			     ["Iowa","Iowa Supreme Court"],
			     ["Iowa Ct. App.","Iowa Court of Appeals"],
			     ["Kan.","Kansas Supreme Court"],
			     ["Kan. Ct. App.","Kansas Court of Appeals"],
			     ["Ky.","Kentucky Supreme Court"],
			     ["Ky. Ct. App.","Kentucky Court of Appeals"],
			     ["La.","Louisiana Supreme Court"],
			     ["La. Ct. App.","Louisiana Court of Appeal"],
			     ["Me.","Maine Supreme Court"],
			     ["Md.","Maryland Supreme Court"],
			     ["Md. Ct. Spec. App.","Maryland Court of Special Appeals"],
			     ["Mass.","Massachusetts Supreme Judicial Court"],
			     ["Mass. App. Ct.","Massachusetts Appeals Court"],
			     ["Mich.","Michigan Supreme Court"],
			     ["Mich. Ct. App.","Michigan Court of Appeals"],
			     ["Minn.","Minnesota Supreme Court"],
			     ["Minn. Ct. App.","Minnesota Court of Appeals"],
			     ["Miss.","Mississippi Supreme Court"],
			     ["Miss. Ct. App.","Mississippi Court of Appeals"],
			     ["Mo.","Missouri Supreme Court"],
			     ["Mo. Ct. App.","Missouri Court of Appeals"],
			     ["Mont.","Montana Supreme Court"],
			     ["Neb.","Nebraska Supreme Court"],
			     ["Neb. Ct. App.","Nebraska Court of Appeals"],
			     ["Nev,","Nevada Supreme Court"],
			     ["N.H.","New Hampshire Supreme Court"],
			     ["N.J.","New Jersey Supreme Court"],
			     ["N.J. Super. Ct. App. Div.","New Jersey Superior Court, Appellate Divsion"],
			     ["N.M.","New Mexico Supreme Court"],
			     ["N.M. Ct. App.","New Mexico Court of Appeals"],
			     ["N.Y.","New York Court of Appeals"],
			     ["N.Y. App. Div.","New York Supreme Court, Appellate Division"],
			     ["N.C.","North Carolina Supreme Court"],
			     ["N.C. Ct. App.","North Carolina Court of Appeals"],
			     ["N.D","North Dakota Supreme Court"],
			     ["N.D. Ct. App","Court of Appeals of North Dakota"],
			     ["Ohio","Ohio Supreme Court"],
			     ["Ohio Ct. App.","Ohio Court of Appeals"],
			     ["Okla.","Oklahoma Supreme Court"],
			     ["Okla. Crim. App.","Oklahoma Court of Criminal Appeals"],
			     ["Okla. Civ. App.","Oklahoma Court of Civil Appeals"],
			     ["Or.","Oregon Supreme Court"],
			     ["Or. Ct. App.","Oregon Court of Appeals"],
			     ["Pa.","Pennsylvania Supreme Court"],
			     ["Pa. Super. Ct.","Pennsylvania Superior Court"],
			     ["R.I.","Rhode Island Supreme Court"],
			     ["S.C.","South Carolina Supreme Court"],
			     ["S.C. Ct. App.","South Carolina Court of Appeals"],
			     ["S.D.","South Dakota Supreme Court"],
			     ["Tenn.","Tennessee Supreme Court"],
			     ["Tenn. Ct. App.","Tennessee Court of Appeals"],
			     ["Tex.","Texas Supreme Court"],
			     ["Tex. Crim. App.","Texas Court of Criminal Appeals"],
			     ["Tex. App.","Texas Courts of Appeals"],
			     ["Utah","Utah Supreme Court"],
			     ["Utah Ct. App.","Utah Court of Appeals"],
			     ["Vt.","Vermont Supreme Court"],
			     ["Va. ","Virginia Supreme Court"],
			     ["Va. Ct. App.","Virginia Court of Appeals"],
			     ["Wash.","Washington Supreme Court"],
			     ["Wash. Ct. App.","Washington Court of Appeals"],
			     ["W. Va.","West Virginia Supreme Court of Appeals"],
			     ["Wis.","Wisconsin Supreme Court"],
			     ["Wis. Ct. App.","Wisconsin Court of Appeals"],
			     ["Wyo.","Wyoming Supreme Court"]]

## add state court abbreviations to court reporter list

for triple in State_court_abbreviations:
        variants =get_abbrev_variation(triple[0])
        standard = variants[0]
        for variant in variants:
            if variant:
                v = regexp_friendly_variant(variant)
                if not v in court_reporter_rexp_list:
                    court_reporter_rexp_list.append(v)
		    ## court_reporter_rexp=court_reporter_rexp+'|'
                    ## court_reporter_rexp = court_reporter_rexp+regexp_friendly_variant(variant)
        result=[standard]
        for variant in variants:
                if variant:
                        court_reporter_abbreviation_table[variant.upper()]=result
                        court_reporter_standard_table[variant.upper()]=standard.upper()



 # other info

 # Fla. Stat. Florida Statutes
 # Fla. Stat. Ann. Florida Statutes Annotated
 # Stat. Statutes at Large
 # U.S.C. United States Code

 ## table -- keys = abbreviations used in citations
 ##       -- values = [court_listener_directory,full_name]

 ## from court_listener_directories.tsv

court_abbrev_table = {}

for cit_abbrev, cl_abbrev, full_form in [['scotus', 'scotus','supreme court of the united states'], ## don't know abbrev
['1st cir.', 'ca1','court of appeals for the first circuit'],
['2d cir.', 'ca2','court of appeals for the second circuit'],
['3rd cir.', 'ca3','court of appeals for the third circuit'],
['4th cir.', 'ca4','court of appeals for the fourth circuit'],
['5th cir.', 'ca5','court of appeals for the fifth circuit'],
['6th cir.', 'ca6','court of appeals for the sixth circuit'],
['7th cir.', 'ca7','court of appeals for the seventh circuit'],
['8th cir.', 'ca8','court of appeals for the eighth circuit'],
['9th cir.', 'ca9','court of appeals for the ninth circuit'],
['10th cir.', 'ca10','court of appeals for the tenth circuit'],
['11th cir.', 'ca11','court of appeals for the eleventh circuit'],
['d.c. cir.', 'cadc','court of appeals for the d.c. circuit'],
['fed. cir.', 'cafc','court of appeals for the federal circuit'],
['a.f.c.c.a.', 'afcca','united states air force court of criminal appeals'],
['ct. cl.', 'cc','united states court of claims'],
['cc', 'cc','united states court of claims'],
['cca','none','us circuit court of appeals'],  ### seems to be ambiguous among (13?) circuit courts, but disambiguated by an additional number
['ca','none','us circuit court of appeals'],  ### seems to be ambiguous among (13?) circuit courts, but disambiguated by an additional number
['fed. cl.', 'uscfc','united states court of federal claims'],
['c.c.p.a.', 'ccpa','court of customs and patent appeals'],
['cust. ct.', 'cusc','united states customs court'],
['tax ct.', 'tax','united states tax court'],
['m.c.', 'mc','united states court of military commission review'],
['mspb', 'mspb','merit systems protection board'], ## don't know abbrev
['vet. app.', 'cavc','united states court of appeals for veterans claims'],
['regl. rail reorg. act', 'reglrailreorgct','special court under the regional rail reorganization act'],
['ct. intl. trade', 'cit','united states court of international trade'],
['1st cir. bap', 'bap1','bankruptcy appellate panel of the first circuit'],
['2d cir. bap', 'bap2','bankruptcy appellate panel of the second circuit'],
['6th cir. bap', 'bap6','bankruptcy appellate panel of the sixth circuit'],
['8th cir. bap', 'bap8','united states bankruptcy appellate panel for the eighth circuit'],
['9th cir. bap', 'bap9','united states bankruptcy appellate panel for the ninth circuit'],
['10th cir. bap', 'bap10','bankruptcy appellate panel of the tenth circuit'],
['mass. bap', 'bapma','bankruptcy appellate panel of massachusetts'],
['bankr. m.d. ala.', 'almb','united states bankruptcy court, m.d. alabama'],
['bankr. n.d. ala.', 'alnb','united states bankruptcy court, n.d. alabama'],
['bankr. s.d. ala.', 'alsb','united states bankruptcy court, s.d. alabama'],
['bankr. d. alaska', 'akb','united states bankruptcy court, d. alaska'],
['bankr. d. ariz.', 'arb','united states bankruptcy court, d. arizona'],
['bankr. e.d. ark.', 'areb','united states bankruptcy court, e.d. arkansas'],
['bankr. w.d. ark.', 'arwb','united states bankruptcy court, w.d. arkansas'],
['bankr. c.d. cal.', 'cacb','united states bankruptcy court, c.d. california'],
['bankr. e.d. cal.', 'caeb','united states bankruptcy court, e.d. california'],
['bankr. n.d. cal.', 'canb','united states bankruptcy court, n.d. california'],
['bankr. s.d. cal.', 'casb','united states bankruptcy court, s.d. california'],
['bankr.d. colo.', 'cob','united states bankruptcy court, d. colorado'],
['bankr. d. conn.', 'ctb','united states bankruptcy court, d. connecticut'],
['bankr. d. del.', 'deb','united states bankruptcy court, d. delaware'],
['bankr. d.c.', 'dcb','united states bankruptcy court, district of columbia'],
['bankr. m.d. fla.', 'flmb','united states bankruptcy court, m.d. florida'],
['bankr. n.d. fla.', 'flnb','united states bankruptcy court, n.d. florida'],
['bankr. s.d. florida', 'flsb','united states bankruptcy court, s.d. florida.'],
['bankr. m.d. ga.', 'gamb','united states bankruptcy court, m.d. georgia'],
['bankr. n.d. ga.', 'ganb','united states bankruptcy court, n.d. georgia'],
['bankr. s.d. ga.', 'gasb','united states bankruptcy court, s.d. georgia'],
['bankr. d. haw.', 'hib','united states bankruptcy court, d. hawaii'],
['bankr. d. idaho', 'idb','united states bankruptcy court, d. idaho'],
['bankr. c.d. ill.', 'ilcb','united states bankruptcy court, c.d. illinois'],
['bankr. n.d. ill.', 'ilnb','united states bankruptcy court, n.d. illinois'],
['bankr. s.d. ill.', 'ilsb','united states bankruptcy court, s.d. illinois'],
['bankr. n.d. ind.', 'innb','united states bankruptcy court, n.d. indiana'],
['bankr. s.d. ind.', 'insb','united states bankruptcy court, s.d. indiana'],
['bankr. d. iowa', 'ianb','united states bankruptcy court, n.d. iowa'],
['bankr. s.d. iowa', 'iasb','united states bankruptcy court, s.d. iowa'],
['bankr. d. kan.', 'ksb','united states bankruptcy court, d. kansas'],
['bankr. e.d. ky.', 'kyeb','united states bankruptcy court, e.d. kentucky'],
['bankr. w.d. ky.', 'kywb','united states bankruptcy court, w.d. kentucky'],
['bankr. e.d. la.', 'laeb','united states bankruptcy court, e.d. louisiana'],
['bankr. m.d. la.', 'lamb','united states bankruptcy court, m.d. louisiana'],
['bankr. w.d. la.', 'lawb','united states bankruptcy court, w.d. louisiana'],
['bankr. d. me.', 'meb','united states bankruptcy court, d. maine'],
['bankr. d. md.', 'mdb','united states bankruptcy court, d. maryland'],
['bankr. d. mass.', 'mab','united states bankruptcy court, d. massachusetts'],
['bankr. e.d. mich.', 'mieb','united states bankruptcy court, e.d. michigan'],
['bankr. w.d. mich.', 'miwb','united states bankruptcy court, w.d. michigan'],
['bankr. d. minn.', 'mnb','united states bankruptcy court, d. minnesota'],
['bankr. n.d. miss.', 'msnb','united states bankruptcy court, n.d. mississippi'],
['bankr. s.d. miss.', 'mssb','united states bankruptcy court, s.d. mississippi'],
['bankr. e.d. mo.', 'moeb','united states bankruptcy court, e.d. missouri'],
['bankr. w.d. mo.', 'mowb','united states bankruptcy court, w.d. missouri'],
['bankr. d. mont.', 'mtb','united states bankruptcy court, d. montana'],
['bankr. d. neb.', 'nebraskab','united states bankruptcy court, d. nebraska'],
['bankr. d. nev.', 'nvb','united states bankruptcy court, d. nevada'],
['bankr. d.n.h.', 'nhb','united states bankruptcy court, d. new hampshire'],
['bankr. d.n.j.', 'njb','united states bankruptcy court, d. new jersey'],
['bankr. d.n.m.', 'nmb','united states bankruptcy court, d. new mexico'],
['bankr. e.d.n.y.', 'nyeb','united states bankruptcy court, e.d. new york'],
['bankr. n.d.n.y.', 'nynb','united states bankruptcy court, n.d. new york'],
['bankr. s.d.n.y.', 'nysb','united states bankruptcy court, s.d. new york'],
['bankr. w.d.n.y.', 'nywb','united states bankruptcy court, w.d. new york'],
['bankr. e.d.n.c.', 'nceb','united states bankruptcy court, e.d. north carolina'],
['bankr. m.d.n.c.', 'ncmb','united states bankruptcy court, m.d. north carolina'],
['bankr. w.d.n.c.', 'ncwb','united states bankruptcy court, w.d. north carolina'],
['bankr. d.n.d.', 'ndb','united states bankruptcy court, d. north dakota'],
['bankr. n.d. ohio', 'ohnb','united states bankruptcy court, n.d. ohio'],
['bankr. s.d. ohio', 'ohsb','united states bankruptcy court, s.d. ohio'],
['bankr. e.d. okla.', 'okeb','united states bankruptcy court, e.d. oklahoma'],
['bankr. n.d. okla', 'oknb','united states bankruptcy court, n.d. oklahoma'],
['bankr. w.d. okla.', 'okwb','united states bankruptcy court, w.d. oklahoma'],
['bankr. d. or.', 'orb','united states bankruptcy court, d. oregon'],
['bankr. e.d. pa.', 'paeb','united states bankruptcy court, e.d. pennsylvania'],
['bankr. m.d. penn.', 'pamb','united states bankruptcy court, m.d. pennsylvania'],
['bankr. w.d. pa.', 'pawb','united states bankruptcy court, w.d. pennsylvania'],
['bankr. d.r.i.', 'rib','united states bankruptcy court, d. rhode island'],
['bankr. d.s.c.', 'scb','united states bankruptcy court, d. south carolina'],
['bankr. d.s.d.', 'sdb','united states bankruptcy court, d. south dakota'],
['bankr. e.d. tenn.', 'tneb','united states bankruptcy court, e.d. tennessee'],
['bankr. m.d. tenn.', 'tnmb','united states bankruptcy court, m.d. tennessee'],
['bankr. w.d. tenn.', 'tnwb','united states bankruptcy court, w.d. tennessee'],
['bankr. d. tenn.', 'tennesseeb','united states bankruptcy court, d. tennessee'],
['bankr. e.d. tex.', 'txeb','united states bankruptcy court, e.d. texas'],
['bankr. n.d. tex.', 'txnb','united states bankruptcy court, n.d. texas'],
['bankr. s.d. tex.', 'txsb','united states bankruptcy court, s.d. texas'],
['bankr. w.d. tex.', 'txwb','united states district court, w.d. texas'],
['bankr. d. utah', 'utb','united states bankruptcy court, d. utah'],
['bankr. d. vt.', 'vtb','united states bankruptcy court, d. vermont'],
['bankr. e.d. va.', 'vaeb','united states bankruptcy court, e.d. virginia'],
['bankr. w.d. va.', 'vawb','united states bankruptcy court, w.d. virginia'],
['bankr. e.d. wash.', 'waeb','united states bankruptcy court, e.d. washington'],
['bankr. w.d. wash.', 'wawb','united states bankruptcy court, w.d. washington'],
['bankr. n.d.w. va.', 'wvnb','united states district court, n.d. west virginia'],
['bankr. s.d.w. va.', 'wvsb','united states bankruptcy court, s.d. west virginia'],
['bankr. e.d. wis.', 'wieb','united states bankruptcy court, e.d. wisconsin'],
['bankr. w.d. wis.', 'wiwb','united states bankruptcy court, w.d. wisconsin'],
['bankr. d. wyo.', 'wyb','united states bankruptcy court, d. wyoming'],
['bankr. d. guam', 'gub','united states bankruptcy court, d. guam'],
['bankr. n. mar. i.', 'nmib','united states bankruptcy court, northern mariana islands'],
['bankr. d.p.r.', 'prb','united states bankruptcy court, d. puerto rico'],
['bankr. d.v.i.', 'vib','united states bankruptcy court, d. virgin islands'],
	## ['d.c.', 'dcd','district court, district of columbia'],  ### this would make 'd.c.' be an ambiguous reference
	## but this seems to be what is stated in the court listener tables online
['d.d.c.', 'dcd','district court, district of columbia'],
['acca', 'acca','army court of criminal appeals'], ## don't know abbrev
['ala', 'ala','supreme court of alabama'],
['ala. civ. app.', 'alacivapp','court of civil appeals of alabama'],
['ala. crim. app.', 'alacrimapp','court of criminal appeals of alabama'],
['ala. ct. app.', 'alactapp','alabama court of appeals'],
['ala. dist. ct.', 'ald','district court, d. alabama'],
['alaska ct. app.', 'alaskactapp','court of appeals of alaska'],
['alaska', 'alaska','alaska supreme court'],
['ariz. ct. app.', 'arizctapp','court of appeals of arizona'],
['ariz. t.c.', 'ariztaxct','arizona tax court'],
['ariz.', 'ariz','arizona supreme court'],
['ark. ct. app.', 'arkctapp','court of appeals of arkansas'],
['ark.', 'ark','supreme court of arkansas'],
['armfor', 'armfor','court of appeals for the armed forces'], ## don't know abbrev
['asbca', 'asbca','armed services board of contract appeals'], ## don't know abbrev
['bapme', 'bapme','bankruptcy appellate panel, d. maine'], ## don't know abbrev
['bva', 'bva','board of veterans\' appeals'], ## don't know abbrev
['c.d. cal.', 'cacd','district court, c.d. california'],
['c.d. ill.', 'ilcd','district court, c.d. illinois'],
['c.d. mo.', 'mocd','district court, c.d. missouri'],
['cal. cir.', 'caca','circuit court for california'],
['cal. ct. app.', 'calctapp','california court of appeal'],
['cal.', 'cal','california supreme court'],
['colo', 'colo','supreme court of colorado'],
['colo. ct. app.', 'coloctapp','colorado court of appeals'],
['com', 'com','commerce court'], ## don't know abbrev
['conn. app. ct.', 'connappct','connecticut appellate court'],
['conn. super. ct.', 'connsuperct','connecticut superior court'],
['conn.', 'conn','supreme court of connecticut'],
['ct. jud. del.', 'deljudct','court on the judiciary of delaware.'],
['ct. jud. disc. pa', 'cjdpa','court of judicial discipline of pennsylvania'],
['d. alaska', 'akd','district court, d. alaska'],
['d. ariz.', 'azd','district court, d. arizona'],
['d. cal.', 'californiad','district court, d. california'],
['d. colo.', 'cod','district court, d. colorado'],
['d. conn.', 'ctd','district court, d. connecticut'],
['d. del.', 'ded','district court, d. delaware'],
['d. guam', 'gud','district court, d. guam'],
['d. haw.', 'hid','district court, d. hawaii'],
['d. idaho', 'idd','district court, d. idaho'],
['d. ill.', 'illinoisd','district court, d. illinois'],
['d. ind.', 'indianad','district court, d. indiana'],
['d. kan.', 'ksd','district court, d. kansas'],
['d. maryland', 'mdd','district court, d. maryland'],
['d. mass.', 'mad','district court, d. massachusetts'],
['d. md.','mdd','district of maryland'],
['d. me.', 'med','district court, d. maine'],
['d. minnesota', 'mnd','district court, d. minnesota'],
['d. min.', 'mnd','district court, d. minnesota'],
['d. mont.', 'mtd','district court, d. montana'],
['d. neb.', 'ned','district court, d. nebraska'],
['d. nev.', 'nvd','district court, d. nevada'],
['d. ohio', 'ohiod','district court, d. ohio'],
['d. or.', 'ord','district court, d. oregon'],
['d. pa.', 'pennsylvaniad','district court, d. pennsylvania'],
['d. tenn.', 'tennessed','district court, d. tennessee'],
['d. tex', 'texd','district court, d. texas'],
['d. utah', 'utd','united states district court, d. utah'],
['d. vt.', 'vtd','district court, d. vermont'],
['d. wash', 'washd','district court, d. washington'],
['e.d. wis.', 'wied','district court, e.d. wisconsin'],
['d. wis.', 'wied','district court, d. wisconsin'], ## unclear if this is correct
['d. wyo.', 'wyd','district court, d. wyoming'],
['d.c.', 'dc','district of columbia court of appeals'],
['d.c.z.', 'canalzoned','district court, canal zone'],
['d.n.c.', 'ncd','district court, d. north carolina'],
['d.n.d.', 'ndd','district court, d. north dakota'],
['d.n.h.', 'nhd','district court, d. new hampshire'],
['d.n.j.', 'njd','district court, d. new jersey'],
['d.n.m.', 'nmd','district court, d. new mexico'],
['d.p.r.', 'prd','district court, d. puerto rico'],
['d.r.i.', 'rid','district court, d. rhode island'],
['d.s.c.', 'scd','united states district court, d. south carolina'],
['d.s.d.', 'sdd','district court, d. south dakota'],
['d.v.i.', 'vid','district court, virgin islands'],
['d.w. va.', 'wvad','district court, d. west virginia'],
['del. ch.', 'delch','court of chancery of delaware'],
['del. ct. com. pl.', 'delctcompl','delaware court of common pleas'],
['del. fm. ct.', 'delfamct','delaware family court'],
['del. super. ct.', 'delsuperct','superior court of delaware'],
['del.', 'del','supreme court of delaware'],
['e.d. ark.', 'ared','district court, e.d. arkansas'],
['e.d. cal.', 'caed','district court, e.d. california'],
['e.d. ill.', 'illinoised','district court, e.d. illinois'],
['e.d. ky.', 'kyed','district court, e.d. kentucky'],
['e.d. la.', 'laed','district court, e.d. louisiana.'],
['e.d. mich.', 'mied','district court, e.d. michigan'],
['e.d. mo.', 'moed','district court, e.d. missouri'],
['e.d. okla.', 'oked','district court, e.d. oklahoma'],
['e.d. pa.', 'paed','district court, e.d. pennsylvania'],
['e.d. tenn.', 'tned','district court, e.d. tennessee'],
['e.d. tex', 'txed','district court, d. texas'],
['e.d. va.', 'vaed','district court, e.d. virginia'],
['e.d. wash', 'waed','district court, e.d. washington'],
['e.d.n.c.', 'nced','district court, e.d. north carolina'],
['e.d.n.y', 'nyed','district court, e.d. new york'],
['e.d.s.c.', 'southcarolinaed','district court, e.d. south carolina'],
['eca', 'eca','emergency court of appeals'],# # don't know abbrev
['fisc', 'fisc','foreign intelligence surveillance court'], ## don't know abbrev
['fiscr', 'fiscr','foreign intelligence surveillance court of review'], ## don't know abbrev
['fla', 'fla','supreme court of florida'],
['fla. dist. ct. app.', 'fladistctapp','district court of appeal of florida'],
['fla. dist. ct.', 'fld','district court, d. florida'],
['ga', 'ga','supreme court of georgia'],
['ga. ct. app.', 'gactapp','court of appeals of georgia.'],
['ga. dist. ct.', 'gad','district court, d. georgia'],
['haw. app.', 'hawapp','hawaii intermediate court of appeals'],
['haw.', 'haw','hawaii supreme court'],
['idaho ct. app.', 'idahoctapp','idaho court of appeals'],
['idaho', 'idaho','idaho supreme court'],
['ill. app. ct.', 'illappct','appellate court of illinois'],
['ill.', 'ill','illinois supreme court'],
['ind', 'ind','indiana supreme court'],
['ind. ct. app.', 'indctapp','indiana court of appeals'],
['ind. t.c.', 'indtc','indiana tax court'],
['iowa ct. app.', 'iowactapp','court of appeals of iowa'],
['iowa dist. ct.', 'iad','district court, d. iowa'],
['iowa', 'iowa','supreme court of iowa'],
['j.p.m.l.', 'jpml','united states judicial panel on multidistrict litigation'],
['kan. ct. app.', 'kanctapp','court of appeals of kansas'],
['kan.', 'kan','supreme court of kansas'],
['ky. ct. app.', 'kyctapp','court of appeals of kentucky'],
['ky.', 'ky','kentucky supreme court'],
['la', 'la','supreme court of louisiana'],
['la. ct. app.', 'lactapp','louisiana court of appeal'],
['la. dist. ct.', 'lad','district court, d. louisiana'],
['m.d. ala.', 'almd','district court, m.d. alabama'],
['m.d. fla.', 'flmd','district court, m.d. florida'],
['m.d. la.', 'lamd','district court, m.d. louisiana'],
['m.d. penn.', 'pamd','district court, m.d. pennsylvania'],
['m.d. pa.', 'pamd','district court, m.d. pennsylvania'],
['m.d. tenn.', 'tnmd','district court, m.d. tennessee'],
['m.d.n.c.', 'ncmd','district court, m.d. north carolina'],
['mass. app. ct.', 'massappct','massachusetts appeals court'],
['mass. dist. ct.', 'massdistct','massachusetts district court'],
['mass. super. ct.', 'masssuperct','massachusetts superior court'],
['mass.', 'mass','massachusetts supreme judicial court'],
['md. ct. spec. app.', 'mdctspecapp','court of special appeals of maryland'],
['md.', 'md','court of appeals of maryland'],
['me.', 'me','supreme judicial court of maine'],
['mich. ct. app.', 'michctapp','michigan court of appeals'],
['mich. dist. ct.', 'michd','district court, d. michigan'],
['mich.', 'mich','michigan supreme court'],
['minn. ct. app.', 'minnctapp','court of appeals of minnesota'],
['minn.', 'minn','supreme court of minnesota'],
['miss. ct. app.', 'missctapp','court of appeals of mississippi'],
['miss. dist. ct.', 'missd','district court, d. mississippi'],
['miss.', 'miss','mississippi supreme court'],
['mo. ct. app.', 'moctapp','missouri court of appeals'],
['mo. dist. ct.', 'mod','district court, d. missouri'],
['mo. s.d.', 'mosd','district court, s.d. missouri'],
['mo.', 'mo','supreme court of missouri'],
['mont.', 'mont','montana supreme court'],
['n. mar. i.', 'nmid','district court, northern mariana islands'],
['d.n. mar. i.', 'nmid','district court, northern mariana islands'],
['n.c. ct. app.', 'ncctapp','court of appeals of north carolina'],
['n.c.', 'nc','supreme court of north carolina'],
['n.d. ala.', 'alnd','district court, n.d. alabama'],
['n.d. cal.', 'cand','district court, n.d. california'],
['n.d. ct. app.', 'ndctapp','north dakota court of appeals'],
['n.d. fla.', 'flnd','district court, n.d. florida'],
['n.d. ga', 'gand','district court, n.d. georgia'],
['m.d. ga', 'gamd','district court, m.d. georgia'],
['n.d. ill.', 'ilnd','district court, n.d. illinois'],
['n.d. ind.', 'innd','district court, n.d. indiana'],
['n.d. iowa', 'iand','district court, n.d. iowa'],
['n.d. miss.', 'msnd','district court, n.d. mississippi'],
['n.d. ohio', 'ohnd','district court, n.d. ohio'],
['n.d. okla.', 'oknd','district court, n.d. oklahoma'],
['n.d. tex.', 'txnd','district court, n.d. texas'],
['n.d.', 'nd','north dakota supreme court'],
['n.d.n.y', 'nynd','district court, n.d. new york'],
['n.d.w. va.', 'wvnd', 'district court, n.d. west virginia'],
['n.h.', 'nh','supreme court of new hampshire'],
['n.j. super. ct. app. div.', 'njsuperctappdiv','new jersey superior court'],
['n.j. tax ct.', 'njtaxct','new jersey tax court'],
['n.m. ct. app.', 'nmctapp','new mexico court of appeals'],
['n.y. app. div.', 'nyappdiv','appellate division of the supreme court of the state of new york'],
['n.y. app. term.', 'nyappterm','appellate terms of the supreme court of new york'],
['n.y. fam. ct.', 'nyfamct','new york family court'],
['n.y. sup. ct.', 'nysupct','new york supreme court'],
['n.y. sur. ct.', 'nysurct','new york surrogate\'s court'],
['neb. ct. app.', 'nebctapp','nebraska court of appeals'],
['neb.', 'neb','nebraska supreme court'],
['nev', 'nev','nevada supreme court'],
['nj', 'nj','supreme court of new jersey'],
['nm', 'nm','new mexico supreme court'],
['nmcca', 'nmcca','navy-marine corps court of criminal appeals'], ## don't know abbrev
['ny', 'ny','new york court of appeals'],
['ny. dist. ct.', 'nyd','district court, d. new york'],
['ohi', 'ohi','ohio supreme court'],
['ohio ct. app.', 'ohioctapp','ohio court of appeals'],
['ohio ct. cl.', 'ohioctcl','ohio court of claims'],
['okla. att’y gen.', 'oklaag','oklahoma attorney general reports'],
['okla. c.o.j.', 'oklacoj','court on the judiciary of oklahoma'],
['okla. civ. app.', 'oklacivapp','court of civil appeals of oklahoma'],
['okla. crim. app.', 'oklacrimapp','court of criminal appeals of oklahoma'],
['okla. j.e.a.p.', 'oklajeap','oklahoma judicial ethics advisory panel'],
['okla.', 'okla','supreme court of oklahoma'],
['or. ct. app.', 'orctapp','court of appeals of oregon'],
['or.', 'or','oregon supreme court'],
['orld', 'orld','district court, orleans'],  # might be the same as opcdc, but don't know abbrev
['pa. commw. ct.', 'pacommwct','commonwealth court of pennsylvania'],
['pa. super. ct.', 'pasuperct','superior court of pennsylvania'],
['pa.', 'pa','supreme court of pennsylvania'],
['r.i.', 'ri','supreme court of rhode island'],
['s.c. ct. app.', 'scctapp','court of appeals of south carolina'],
['s.c.', 'sc','supreme court of south carolina'],
['s.d. ala.', 'alsd','district court, s.d. alabama'],
['s.d. cal.', 'casd','district court, s.d. california'],
['s.d. fla.', 'flsd','district court, s.d. florida'],
['s.d. ga.', 'gasd','district court, s.d. georgia'],
['s.d. ill.', 'ilsd','district court, s.d. illinois'],
['s.d. ind.', 'insd','district court, s.d. indiana'],
['s.d. iowa', 'iasd','district court, s.d. iowa'],
['s.d. miss.', 'mssd','district court, s.d. mississippi'],
['s.d. ohio', 'ohsd','district court, s.d. ohio'],
['s.d. tex.', 'txsd','district court, s.d. texas'],
['s.d.', 'sd','south dakota supreme court'],
['s.d.n.y.', 'nysd','district court, s.d. new york'],
['s.d.w. va', 'wvsd','district court, s.d. west virginia.'],
['special tribunal of pa.', 'stp','united states special tribunal of pennsylvania'],
['tecoa', 'tecoa','temporary emergency court of appeals'], ## don't know abbrev
['tenn. crim. app.', 'tenncrimapp','court of criminal appeals of tennessee'],
['tenn. ct. app.', 'tennctapp','court of appeals of tennessee'],
['tenn.', 'tenn','tennessee supreme court'],
['tex. app.', 'texapp','court of appeals of texas'],
['tex. crim. app.', 'texcrimapp','court of criminal appeals of texas'],
['tex. rev.', 'texreview','texas special court of review'],
['tex.', 'tex','texas supreme court'],
['u.s.j.c.', 'usjc','united states judicial conference committee'],
['utah ct. app.', 'utahctapp','court of appeals of utah'],
['utah', 'utah','utah supreme court'],
['va. ct. app.', 'vactapp','court of appeals of virginia'],
['va. dist. ct.', 'vad','district court, d. virginia'],
['va.', 'va','supreme court of virginia'],
['vt.', 'vt','supreme court of vermont'],
['w. va.', 'wva','west virginia supreme court'],
['w.d. ark.', 'arwd','district court, w.d. arkansas'],
['w.d. ky.', 'kywd','district court, w.d. kentucky'],
['w.d. la.', 'lawd','district court, w.d. louisiana'],
['w.d. mich.', 'miwd','district court, w.d. michigan'],
['w.d. mo.', 'mowd','district court, w.d. missouri'],
['w.d. okla.', 'okwd','district court, w.d. oklahoma'],
['w.d. pa.', 'pawd','district court, w.d. pennsylvania'],
['w.d. tenn.', 'tnwd','district court, w.d. tennessee'],
['w.d. tex.', 'txwd','district court, w.d. texas'],
['w.d. va.', 'vawd','district court, w.d. virginia'],
['w.d. wash.', 'wawd','district court, w.d. washington'],
['w.d. wis.', 'wiwd','district court, w.d. wisconsin'],
['w.d.n.c.', 'ncwd','district court, w.d. north carolina'],
['w.d.n.y.', 'nywd','district court, w.d. new york'],
['w.d.s.c.', 'southcarolinawd','district court, w.d. south carolina'],
['wash. ct. app.', 'washctapp','court of appeals of washington'],
['wash.', 'wash','washington supreme court'],
['wis. ct. app.', 'wisctapp','court of appeals of wisconsin'],
['wis. dist. ct.', 'wisd','district court, d. wisconsin'],
['wis.', 'wis','wisconsin supreme court'],
['wyo.', 'wyo','wyoming supreme court']
]:
    variants = get_abbrev_variation(cit_abbrev)
    variants.append(cl_abbrev) ## this seems to be used also
    standard = variants[0].upper()
    for variant in variants:
	    if variant:
		    variant = variant.upper()
		    court_abbrev_table[variant] = standard
		    ## ignoring cl_abbrev and full_form

## REPORTERS --use variants only
## each variations key maps some set of variants to the original
## In the 2 entry cases, we should allow the variants to be the same as each other
## unless they conflict with the first entry.
## 1) We should use these "variants" fields to update our tables at the bottom of this file
## 2) For one entry cases, this is simple
## 3) For 2 entry cases, we should be careful not to combine to different entries together
## 4) Tables to update
##    a) court_reporter_abbreviation_table
##    b) court_reporter_standard_table
## 5) regexp to update: court_reporter_rexp

## note everything in tables are upper case
def process_jurisdict(juris,name):
    if len(juris)>1:
        return('Various')
    elif len(juris) == 0:
        return('Unspecified')
    elif (not ':' in juris[0]):
        return(re.sub('[:\.]',' ',juris[0]))
    else:
        items = juris[0].partition(':')
        return(re.sub('[:\.]',' ',items[-1]))


cl_reporter_variation_table = {}

def increment_court_reporter_variables(in_dictionary):
    global court_reporter_rexp
    var_dict = in_dictionary['variations']
    if not 'name' in in_dictionary:
        print('???Odd input to increment_court_reporter_variables')
        ## print(in_dictionary)
    name_info = in_dictionary['name']
    jurisdict = process_jurisdict(in_dictionary['mlz_jurisdiction'],name_info)
    name = jurisdict
    reporter = name_info
    if name and reporter:
        name = name.strip(' ')
        reporter = reporter.strip(' ')
    for key,value in var_dict.items():
        variants = get_abbrev_variation(key)
        for v in get_abbrev_variation(value):
            if v:
                v = v.upper()
                if not v in variants:
                    variants.append(v)
        standard = variants[0].upper()
        result = [standard,name,reporter]
        for v in variants:
            if v:
                v = v.upper()
            if v and (not v in court_reporter_abbreviation_table):
                court_reporter_abbreviation_table[v]= result
                court_reporter_standard_table[v]=standard
                v1 = regexp_friendly_variant(v)
                if not v1 in court_reporter_rexp_list:
                    court_reporter_rexp_list.append(v1)
		## court_reporter_rexp=court_reporter_rexp+'|'
                ## court_reporter_rexp = court_reporter_rexp+regexp_friendly_variant(v)

def update_editions (editions,new_edition,edition_number):
    for key in new_edition:
        edition_number += 1
        editions[key+str(edition_number)]=new_edition[key]
    return(edition_number)

def merge_reporter_names (names):
    if len(names) == 1:
        return(names.pop())
    else:
        common_words = []
        for name in names:
            name = re.sub('[^a-zA-Z]',' ',name)
            words = name.split(' ')
            words2 = []
            for word in words:
                if re.search('[a-zA-Z]',word):
                    word = word.capitalize()
                    if not word in ['Report','Reports']:
                        words2.append(word)
            if len(words2)>0:
                if len(common_words) == 0:
                    common_words = words2
                else:
                    common_words2 = []
                    for word in common_words:
                        if word in words2:
                            common_words2.append(word)
                    common_words = common_words2
        if len(common_words)==1:
            return(common_words[0]+' Reports (Ambiguous)')
        else:
            print('Can\'t disambiguate reporter names:',names)
            return('Ambiguous Reports')

def merge_cite_types(cite_types):
    if len(cite_types) == 1:
        return(cite_types.pop())
    else:
        return('ambiguous')
	    

def merge_juris_types(jurisdictions):
    juris_pattern = re.compile('([a-z]+):?([a-z]+)?;([a-z\.]+)')
    countries = set()
    states = set()
    levels = set()
    for juris_set in jurisdictions:
        for juris in juris_set:
            match = juris_pattern.search(juris)
            if not match:
                print(juris,'not well formed.')
            else:
                country = match.group(1)
                state = match.group(2)
                level = match.group(3)
                if not state:
                    states.add('federal')
                else:
                    states.add(state)
                if not country:
                    print('No country in jurisdiction.')
                else:
                    countries.add(country)
                if level:
                    levels.add(level)
    jurisdiction = ''
    if len(countries) == 1:
        jurisdiction = countries.pop()
    if len(states) == 1:
        state = states.pop()
        if state != 'federal':
            jurisdiction += ":"+state
    else:
        jurisdiction += ":ambiguous"
    if len(levels) == 1:
        jurisdiction = jurisdiction + ';' + levels.pop()
    else:
        jurisdiction = jurisdiction + ';' + 'ambiguous'
    return([jurisdiction])
	
def distinguish_dicts(dict_list):
    out_dicts = {}
    merged_dict = {}
    merged_variations = {}
    merged_dict['variations']=merged_variations
    found_variations = []
    duplicate_variations = []
    duplicate_var_keys = set()
    for in_dict in dict_list:
        name = in_dict['name']
        new_dict = in_dict.copy()
        out_dicts[name]=new_dict
        local_variations = new_dict['variations']
        if len(local_variations) == 0:
            new_dict['variations'][name] = name
            found_variations.append(name)
        else:
            values = set(new_dict['variations'].values())
            for value in values:
                if value in found_variations:
                    duplicate_variations.append(value)
                else:
                    found_variations.append(value)
    names = set()
    cite_types = set()
    jurisdictions = []
    editions = {}
    edition_number = 0
    for out_name in out_dicts:
        new_variations = {}
        out_dict = out_dicts[out_name]
        for key in out_dict['variations']:
            if out_dict['variations'][key] in duplicate_variations:
                v_val = out_dict['variations'][key]
                if not key in merged_variations:
                    merged_variations[key]= v_val
            else:
                new_variations[key] = out_dict['variations'][key]
        out_dict['variations'] = new_variations
        cite_types.add(out_dict['cite_type'])
        names.add(out_dict['name'])
        jurisdictions.append(out_dict['mlz_jurisdiction'])
        edition_number  = update_editions(editions,out_dict['editions'],edition_number) 
	## number the keys and then add them to dict
    out_dict_list = []
    for out_name in out_dicts:
        if ('variations' in out_dicts[out_name]) \
           and len(out_dicts[out_name]['variations'])>0:
            out_dict_list.append(out_dicts[out_name])
    if len(merged_variations)>0:
	## variations alreayd set -- now try other features of merged_dict
        merged_dict['name']= merge_reporter_names(names) ## 'ambiguous' + substring + reports
	## ambigous + X or Y reports
        merged_dict['cite_type']= merge_cite_types(cite_types) ## if same, keep same, else X or Y
        merged_dict['mlz_jurisdiction'] = merge_juris_types(jurisdictions) ## similar, except make comparison after : and after ;
        merged_dict['editions'] = editions 
	## add merged_dict to output
        name = merged_dict['name']
        if not name in out_dicts:
            out_dict_list.append(merged_dict)
    else:
        print('??? not duplicate_variations')
    return(out_dict_list)
		
for value in REPORTERS.values():
    if len(value)>1: 
	## These are mostly pretty old
	## We will fudge this by merging them into one value
        ## print('*',value,'*')
        for in_dict in distinguish_dicts(value):
            increment_court_reporter_variables(in_dict)
	# var_dict = {}
	# name_info = 'UNSET_NAME'
        # for v in value:
        #     this_name = v['name']
	#     this_jurisdict = v['jurisdict']
	#     this_reporter = this_name
        #     for feat in v['variations']:
        #         if feat in var_dict:
        #             if v['variations'][feat] ==  var_dict[feat]:
        #                 pass
	# 	    else:
        #                 print('variation conflict')
	# 		print(v['variations'][feat])
	# 		print(var_dict[feat])
	# 	else:
	# 	   var_dict[feat] = var_dict[feat].copy()
    else:
        increment_court_reporter_variables(value[0])

def letter_length(x):
    letter_matches = list(re.finditer('[a-zA-Z]',x))
    non_letter_matches = list(re.finditer('[^a-zA-Z]',x))
    return((len(letter_matches)*-100)+(len(non_letter_matches)*-1))

court_reporter_rexp_list.sort(key = lambda x: letter_length(x))
## sort order causes larger patterns to match before shorter ones (their substrings)

for pattern in court_reporter_rexp_list:
    court_reporter_rexp=court_reporter_rexp+'|'+pattern
court_reporter_rexp=court_reporter_rexp[1:]
## get rid of intial | so the disjunction doesn't match the empty string
