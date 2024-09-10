
table = [["Sun",696000,1989100000],["Earth",6371,5973.6],
         ["Moon",1737,73.5],["Mars",3390,641.85]]

fmt = ["plain", "simple", "github", "grid", "simple_grid", "rounded_grid", "heavy_grid", "mixed_grid", "double_grid", "fancy_grid", "outline", "simple_outline", "rounded_outline", "heavy_outline", "mixed_outline", "double_outline", "fancy_outline", "pipe", "orgtbl", "asciidoc", "jira", "presto", "pretty", "psql", "rst", "mediawiki", "moinmoin", "youtrack", "html", "unsafehtml", "latex", "latex_raw", "latex_booktabs", "latex_longtable", "textile", "tsv"]
t = [tabulate(table, headers=["Planet","R (km)", "mass (x 10^29 kg)"], tablefmt=x) for x in fmt]

print(t[0])
print(type(t))



async def main():
    rec = list(await req.show_reecipes())
    
    l: dict[str:list] = {}
    for r in rec:
        try:
            l[r.recipe_name].append(r)
        except:
            l[r.recipe_name] = []
            l[r.recipe_name].append(r)

    print(l)
    k = list(l.keys())
    for i in k:
        recipe = l[i]
        print(i)
        for ing in recipe:
            print(f"  {ing.ingredient} {ing.weight}")



asyncio.run(main())
