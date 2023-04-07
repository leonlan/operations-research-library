import pandas as pd
import seaborn as sns

sns.set(style="ticks")

problem_name = [
    "Flowshop",
    "Non-Flowshop",
    "Hybridflowshop",
    "Distributedflowshop",
    "Nowaitflowshop",
    "Setupflowshop",
    "Tardinessflowshop",
    "TCTflowshop",
    "Jobshop",
    "Flexiblejobshop",
    "Openshop",
]


dataset = pd.read_excel("results.xlsx", sheet_name="Flowshop")
dataset["type"] = dataset["type"].astype(str).str.strip()
dataset.info()

df1 = dataset  # [(dataset['instance'] >= 121)]
Modeltype = df1["type"].unique()
jobs = df1["n"].unique()
stages = df1["m"].unique()
limit = df1["given"].unique()
print(jobs, stages)

for t in limit:
    df3 = df1[(df1["given"] == t)]
    for model in Modeltype:
        df4 = df3[(df3["type"] == model)]
        for n in jobs:
            for m in stages:
                df2 = df4[(df4["m"] == m) & (df4["n"] == n)]
                if df2.shape[0] >= 1:
                    df = df2[(df2["gap"] >= 0)]
                    if df.shape[0] >= 1:
                        print(
                            model,
                            t,
                            n,
                            m,
                            df.shape[0],
                            df[(df["gap"] == 0)].shape[0],
                            df["gap"].mean(),
                        )
                    else:
                        print(model, t, n, m, 0, 0, 0)
