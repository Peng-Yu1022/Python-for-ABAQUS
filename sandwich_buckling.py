from abaqus import *
from abaqusConstants import *
import regionToolset

session.viewpoint['viewpoint: 1'].setValues(displayedObkect=None)

#--------------------------Create the model-------------------------------------
mdb.models.changekey(fromName='Model-1', toName='Sandwich beam')
sandwichModel = mdb.models['Sandwich beam']

#--------------------------Create the part--------------------------------------
import sketch
import part

beamProfileSketch = sandwichModel.ConstrainedSketch(name = 'beam CS Profile', sheetSize = 5)
rectangleBeam = beamProfileSketch.rectangle(point1=(0,3.63), point2=(1,0))

sandwichPart = sandwichModel.Part(name='core', dimensionality = TWO_D_PLANAR, type = DEFORMABLE_BODY)
sandwichPart.BaseShell(sketch=rectangleBeam)
del beamProfileSketch

horizotal_edges = sandwichPart.edges.findAt(((1.815, 1.0, 0.0),),
                                            ((1.815, 0.0, 0.0),),)
vertical_edges = sandwichPart.edges.findAt(((0,    0.5, 0.0),),
                                           ((3.63, 0.5, 0.0),),)


#--------------------------Define the materials---------------------------------
import material

FacesheetMaterial = sandwichModel.Material(name='Aluminum')
CoreMaterial = sandwichModel.Material('Cork')
FacesheetMaterial.Elastic(table=((10600, 0.33),))
CoreMaterial.Elastic(table=((1.18, 0.136),))

#---------------------------Create solid sections and make section assignment----------------------------
import section

sandwichModel.RectangularProfile(name='rectangle', 2.0, 0.0196)

FacesheetSection = sandwichModel.BeamSection(name='beam section', Profile='rectangle',,material='Aluminum')
CoreSection = sandwichModel.HomogeneousSolidSection(name='core section', material='Cork', thickness=2.0)

horizotal_edges = sandwichPart.edges.findAt(((1.815, 1.0, 0.0),),
                                            ((1.815, 0.0, 0.0),),)
left_end_edge = sandwichPart.edges.findAt(((0, 0.5, 0.0),))
right_end_edge = sandwichPart.edges.findAt(((3.63, 0.5, 0.0),))

#sandwich_face_center = (1.815, 0.5, 0.0)
#sandwich_face = sandwichPart.faces.findAt((sandwich_face_center,))
#Core_region = (sandwich_face,)

Core_region = (sandwichPart.cells,)

sandwichPart.SectionAssignment(region=Core_region, sectionName = 'core section')
Facesheet_region = regionToolset.Region(edges=horizotal_edges)

#-----------------------------------------Create Assembly------------------------------------------------
import assembly

sandwichAssembly = sandwichModel.rootAssembly
sandwichInstance = sandwichAssembly.Instance(name='sandwich instance',part=sandwichPart, dependent = ON)

#-----------------------------------------Create steps---------------------------------------------------
import step

sandwichModel.BuckleStep(name="strained", previous='Initial', numEigen=50, description='displacement is applied')

#--------------------------------------Field Output Requests---------------------------------------------

sandwichModel.fieldOutputRequests.changeKey(fromName='F-Output-1', toName='Selected Field Output')
sandwichModel.fieldOutputRequests['Selected Field Output'].setValues(variables=('S', 'E', 'U', 'RF','CF'))

#--------------------------------------History Output Requests---------------------------------------------

sandwichModel.HistoryOutputRequest(name='Created History Output', createStepName = 'strained', variables=PRESELECT)
del sandwichModel.historyOutputRequest['H-Output-1']

#--------------------------------------------Apply Load--------------------------------------------------

vertex_left_side_middle_coord = (0.0, 0.5, 0.0)
vertex_right_side_middle_coord = (3.63, 0.5, 0.0)
vertex_left_side_middle = sandwichInstance.vertices.findAt((vertex_left_side_middle_coord,))
vertex_right_side_middle = sandwichInstance.vertices.findAt((vertex_right_side_middle_coord,))

#------------------------------------------Apply Boundary-------------------------------------------------

left_end_BC = sandwichModel.DisplcementBC(name='left end', createStepName='Initial', region=(left_end_edge,), u1=0.0)
left_end_middle_BC = sandwichModel.DisplcementBC(name='left_end_middle_BC', createStepName='Initial', region=(vertex_left_side_middle,),u2=0.0)
right_end_middle_BC = sandwichModel.DisplcementBC(name='right end middle point', createStepName='Initial', region=(vertex_right_side_middle,), u2=0.0)
#applying displacement boundary condtion in the following line
right_end_BC = sandwichModel.DisplcementBC(name='right end', createStepName='Initial', region=(right_end_edge,), u1=1.0)

#-----------------------------------------Create Mesh----------------------------------------------------

import mesh

elemType1 = mesh.ElemType(elemCode=CPS4, elemLibrary=STANDARD, )

sandwichPart.seedEdgeByNumber(edges=horizotal_edges, number = 200)
sandwichPart.seedEdgeByNumber(edges=vertical_edges, number = 40)
sandwichPart.generateMesh()

#----------------------------------------Create and run the job------------------------------------------
import job
mdb.Job(name='buckling analysis', model='Sandwich beam', type=ANALYSIS, description=)

mdb.jobs['buckling analysis'].submit(consistencyChecking=OFF)

mdb.jobs['buckling analysis'].waitForCompletion()
