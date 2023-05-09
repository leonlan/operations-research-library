def Distributedflowshopmodel(data, mdl):
    jobs = range(data.n)
    stages = range(data.g)
    factories = range(data.f)

    tasks = [[] for _ in jobs]
    for j in jobs:
        tasks[j] = [[] for _ in stages]

    for j in jobs:
        for i in stages:
            tasks[j][i] = [
                mdl.interval_var(
                    name=f"A_{j}_{i}_{k}",
                    optional=True,
                    size=data.p[j][i],
                )
                for k in factories
            ]

    _tasks = [[] for _ in jobs]

    for j in jobs:
        _tasks[j] = [mdl.interval_var(name=f"T_{j}_{i}") for i in stages]

    for j in jobs:
        for i in stages:
            subexpr = [tasks[j][i][k] for k in factories]
            expr = mdl.alternative(_tasks[j][i], subexpr)
            mdl.add(expr)

    for j in jobs:
        for i in range(1, data.g):
            for k in factories:
                lhs = mdl.presence_of(tasks[j][i][k])
                rhs = mdl.presence_of(tasks[j][0][k])
                mdl.add(lhs >= rhs)

    seq_var = [[]] * data.g
    for i in stages:
        seq_var[i] = [[]] * data.f
        for k in factories:
            seq_var[i][k] = mdl.sequence_var([tasks[j][i][k] for j in jobs])

    for i in stages:
        for k in factories:
            mdl.add(mdl.no_overlap(seq_var[i][k]))  # no overlap machines

    for i in range(data.g - 1):
        for k in factories:
            mdl.add(mdl.same_sequence(seq_var[i][k], seq_var[i + 1][k]))

    for j in jobs:
        for i in range(1, data.g):
            mdl.add(mdl.end_before_start(_tasks[j][i - 1], _tasks[j][i]))

    makespan = mdl.max([mdl.end_of(_tasks[j][data.g - 1]) for j in jobs])
    mdl.add(mdl.minimize(makespan))

    return mdl


"""

 CP Distributedflowshop - 1 - (353 - 758)
84 138	186 265	265 281	287 353	353 411
369 452	452 455	469 558	558 616	680 736
206 221	270 281	358 407	409 440	479 499
221 292	292 391	407 422	440 508	508 593
233 310	315 371	379 468	470 548	556 609
68 104	143 213	220 265	269 360	360 395
104 157	213 312	312 372	372 385	395 448
46 84	126 186	189 212	228 287	287 328
12 39	59 64	122 179	179 228	228 297
452 539	539 595	595 659	659 744	744 757
157 233	312 315	372 379	385 470	470 556
397 488	488 549	558 559	635 644	653 725
32 46	53 126	126 189	189 228	228 236
39 68	68 143	179 220	228 269	297 346
0 12	12 59	59 122	122 178	178 225
292 369	391 405	422 469	508 548	593 680
0 32	32 53	53 79	79 133	133 191
310 397	397 483	483 558	558 635	635 653
138 206	265 270	281 358	358 409	411 479
488 582	582 659	659 699	699 730	730 758
"""
