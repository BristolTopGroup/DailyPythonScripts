from rootpy.io import root_open
from rootpy.tree import Tree, TreeModel, FloatCol
from ROOT import TMVA

class OutputTree(TreeModel):
    classID = FloatCol(default = -1111.)
    var1 = FloatCol(default = -1111.)
    var2 = FloatCol(default = -1111.)
    var3 = FloatCol(default = -1111.)
    weight = FloatCol(default = -1111.)
    cls0 = FloatCol(default = -1111.)
    cls1 = FloatCol(default = -1111.)
    cls2 = FloatCol(default = -1111.)

outfile = root_open('tmva_example_multiple_backgrounds__applied.root', 'recreate' )
output_tree = Tree('multiBkg', model = OutputTree)
r1 = TMVA.Reader( "!Color:!Silent" )
r2 = TMVA.Reader( "!Color:!Silent" )
# r3 = TMVA.Reader( "!Color:!Silent" )

r1.AddVariable('var1', output_tree.var1)
r1.AddVariable('var2', output_tree.var2)
r1.AddVariable('var3', output_tree.var3)

r2.AddVariable('var1', output_tree.var1)
r2.AddVariable('var2', output_tree.var2)
r2.AddVariable('var3', output_tree.var3)

# r3.AddVariable('var1', output_tree.var1)
# r3.AddVariable('var2', output_tree.var2)
# r3.AddVariable('var3', output_tree.var3)

r1.BookMVA('Likelihood::Likelihood', 'weights/MVA_BkgSingleTop_Likelihood.weights.xml')
r1.BookMVA('Likelihood::Likelihood', 'weights/MVA_BkgVJets_Likelihood.weights.xml')
# r1.BookMVA('Likelihood::Likelihood', 'weights/MVA_BkgQCD_Likelihood.weights.xml')
# fill tree

output_tree.write()
outfile.close()


