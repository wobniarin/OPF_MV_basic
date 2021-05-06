


exec(open('model.py').read())
exec(open('data.py').read())
# exec(open('spn33n_data.dat').read())

results = []
solver = SolverFactory('ipopt')
# Create a model instance and optimize
instance = model.create_instance('spn33n_data.dat')
solver.solve(instance)
results.append([model.V2])

results = pd.DataFrame(results, columns=['V2'])

print(results)
datatoexcel=pd.ExcelWriter('resultsV2.xlsx',engine='xlsxwriter')
results.to_excel(datatoexcel,sheet_name='Sheet1')
datatoexcel.save()

