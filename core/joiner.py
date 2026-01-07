def join_bkpf_bseg(bkpf, bseg):
    return bseg.merge(
        bkpf,
        on=["BUKRS", "BELNR", "GJAHR"],
        how="left",
        suffixes=("_LINE", "_HDR")
    )
