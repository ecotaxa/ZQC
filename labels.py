errors = {
    "global.missing_ecotaxa_table": "#MISSING ecotaxa table",
    "global.qc_not_implemented": "#Not impl",
    "global.missing_column": "#MISSING column",
    "global.bad_zip_file": "#BAD ZIP FILE",
    "global.bad_meta_txt_file": "#BAD TXT FILE",
    "global.missing_meta_txt_file": "#MISSING Meta txt file",
    "global.missing_directory.work": "#MISSING _work DIRECTORY",
    "global.not_numeric": "#NOT NUMERIC",

    "process.frame_type.not_ok" : "#Frame NOT OK",

    "process.bw_ratio.not_ok": "#Ratio NOK",

    "process.pixel_size.not_ok": "#Size NOK",

    "process.raw_files.missing": "#MISSING FILE",
    "process.raw_files.duplicate": "#DUPLICATE FILE",
    "process.raw_files.rename_zip": "#BUG rename zip file",
    "process.raw_files.inconsistent_scan_id": "#Inconsistent Scan ID",

    "process.scan_weight.bug": "#BUG weight",

    "process.post_scan.unprocessed": "#UNPROCESSED",
    "process.post_scan.duplicate.tsv": "#DUPLICATE TSV",
    "process.post_scan.missing.zip": "#MISSING ZIP",
    "process.post_scan.duplicate.zip": "#DUPLICATE ZIP",
    "process.post_scan.rename_zip": "#BUG rename zip file",

    "process.sep_mask.missing": "#MISSING SEP MSK",

    "process.post_sep.unprocessed": "#UNPROCESSED",
    "process.post_sep.not_included": "#SEP MSK NOT INCLUDED",

    #TODO JCE : talk with AMANDA for better understanding of this QC
    "acquisition.sieve.bug.different": "#SIEVE different from others",
    "acquisition.sieve.bug.min_sup_max": "#ACQ MIN > ACQ MAX",
    "acquisition.sieve.bug.min_equ_max": "#ACQ MIN = ACQ MAX",
    "acquisition.sieve.bug.min_dn_dif_max_dn+1_1": "#ACQ MIN (d",
    "acquisition.sieve.bug.min_dn_dif_max_dn+1_2": ") ≠ ACQ MAX (d",
    "acquisition.sieve.bug.min_dn_dif_max_dn+1_3": ")",

    "acquisition.motoda.check.identique": "#Identical Motoda",
    #TODO JCE : talk with AMANDA 2^0==1
    "acquisition.motoda.check.cas1": "#Motoda Fraction ≠ 1 or ≠ ^2",
    "acquisition.motoda.check.cas2": "#Motoda Fraction ≠ ^2",
    
    "acquisition.motoda.comparaison.ko": "#Motoda frac",

    "acquisition.motoda.quality.missing": "#MISSING images",
    "acquisition.motoda.quality.low": "#Images nb LOW : ",
    "acquisition.motoda.quality.high": "#Images nb HIGH : ",
}

sucess = {
    "process.bw_ratio.ok": "Ratio OK",
    "process.raw_files.ok": "Files OK",
    "process.scan_weight.ok": "Weight OK",
    "process.post_scan.ok": "Process OK",
    "process.sep_mask.ok": "Sep mask OK",
    "process.post_sep.ok": "process OK",

    "acquisition.sieve.bug.ok": "sieve OK",
    "acquisition.motoda.check.ok": "Motoda OK",
    "acquisition.motoda.comparaison.ok": "Motoda comparison OK",
    "acquisition.motoda.quality.ok": "Motoda OK",

}
