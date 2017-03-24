import vcs
from my_metrics import add
from cdp.cdp_viewer import OutputViewer

result = add(1, 1)

# Using vcs to visualize the result. This is just to show the viewer.
vcs_canvas = vcs.init(bg=True, geometry=(256, 256))
text = vcs_canvas.createtextcombined()
text.x = 0.5
text.y = 0.5
text.string = str(result)
text.height = 96
text.halign = 'center'
vcs_canvas.plot(text)
vcs_canvas.png('output.png')

viewer = OutputViewer(index_name='My Cool Results')
# 'My Results' is the title of the page in the index. 'Generated File' is the column for each group.
viewer.add_page("My Results", ['Description', 'Generated File'])

viewer.add_group('Results of addition')
viewer.add_row('Result of 1 + 1')
viewer.add_col('Some description for add')
viewer.add_col('output.png', is_file=True)
viewer.add_row('Another Result')
viewer.add_col('Another description for add')
viewer.add_col('output.png', is_file=True)

viewer.add_group('Results of subtraction')
viewer.add_row('Some Result')
viewer.add_col('Some description for sub')
viewer.add_col('output.png', is_file=True)

viewer.generate_viewer()
