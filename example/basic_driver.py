import vcs
from my_metrics import add, sub

result = add(1, 1)

# using vcs to visualize the result. This is just to show the viewer
vcs_canvas = vcs.init(bg=True, geometry=(256, 256))
text = vcs_canvas.createtextcombined()
text.x = 0.5
text.y = 0.5
text.string = str(result)
text.height = 96
text.halign = 'center'
vcs_canvas.plot(text)
vcs_canvas.png('output.png')
