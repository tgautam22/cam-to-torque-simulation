# Figures for cam-to-torque: one animated figure with the mechanism, lift graph and torque graph.
# Nothing is calculated here except turning points for drawing; all values come from calc.run().
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from calc import STEP

CAM_FILL = "#C9CFD2"
LINE = "#3A4348"
PART = "#4B6273"
SPRING = "#8A6A2E"
ACCENT = "#2952C8"
LIFT_COL = "#7A3FB0"
TORQUE_COL = "#2952C8"
GRID = "#E9ECED"
ANGLE_LINE = "#B0B6BA"

FRAME_STEP = 2 # deg between animation frames
CAM_EVERY = 5 # draw every 5th outline point (0.5 deg) to keep the animation light


def _index(theta): # position of an angle in the 0.1 deg arrays
    return int(round((theta % 360) / STEP))


def _circle(cx, cy, r, n=90): # points around a circle, for drawing
    t = np.linspace(0, 2 * np.pi, n)
    return (cx + r * np.cos(t)).round(2), (cy + r * np.sin(t)).round(2)


def _sizes(p): # fixed drawing sizes
    span = p.Rb + p.h + 6 # half-width of the drawing area
    base = np.sqrt((p.Rb + p.Rf) ** 2 - p.d**2) # roller centre height on the base circle
    top = base + p.h + 2.4 * p.Rf + 0.9 * (p.Rb + p.h) # fixed plate the spring pushes against
    sw = max(0.9 * p.Rf, 5) # spring half-width
    return span, base, top, sw


def _frame(r, p, theta): # every part that is redrawn each frame, in drawing order (later = on top)
    span, base, top, sw = _sizes(p)
    i = _index(theta)
    c, s = np.cos(np.radians(theta)), np.sin(np.radians(theta))
    x0, y0 = np.append(r.x0[::CAM_EVERY], r.x0[0]), np.append(r.y0[::CAM_EVERY], r.y0[0]) # closed outline
    cam_x = (x0 * c - y0 * s).round(2) # cam outline turned by theta
    cam_y = (x0 * s + y0 * c).round(2)
    yc = r.y_roller[i] # roller centre height from calc
    rod_top = yc + 2.2 * p.Rf # where the rod meets the spring
    zx = [p.d] + [p.d + (sw if k % 2 else -sw) for k in range(1, 20)] + [p.d] # spring zigzag
    zy = np.linspace(rod_top, top, len(zx)).round(2)
    bx, by = _circle(0, 0, p.Rb, 180)
    rx, ry = _circle(p.d, yc, p.Rf)
    lx = p.d + p.Rf + 4 # lift dimension x position
    text = f"θ = {theta:.0f}°<br>lift {r.lift[i]:.2f} mm<br>compression {r.s[i]:.2f} mm<br>torque {r.T[i]:.2f} N·m"
    return [
        go.Scatter(x=cam_x, y=cam_y), # cam
        go.Scatter(x=bx, y=by), # base circle
        go.Scatter(x=[p.d, p.d], y=[-span, top]), # follower line
        go.Scatter(x=[0], y=[0]), # cam centre O
        go.Scatter(x=[0, -0.7 * p.Rb * s], y=[0, 0.7 * p.Rb * c]), # cam's 0 deg mark
        go.Scatter(x=zx, y=zy), # spring
        go.Scatter(x=[p.d, p.d], y=[yc, rod_top]), # rod
        go.Scatter(x=[p.d - sw, p.d + sw], y=[rod_top, rod_top]), # spring seat
        go.Scatter(x=rx, y=ry), # roller
        go.Scatter(x=[p.d], y=[yc]), # roller centre
        go.Scatter(x=[lx, lx], y=[base, yc]), # lift dimension
        go.Scatter(x=[-span + 1], y=[top - 2], text=[text]), # readout
        go.Scatter(x=[theta], y=[r.lift[i]]), # dot on lift graph
        go.Scatter(x=[theta, theta], y=[min(r.lift.min(), 0), r.lift.max()]), # angle line on lift graph
        go.Scatter(x=[theta], y=[r.T[i]]), # dot on torque graph
        go.Scatter(x=[theta, theta], y=[r.T.min(), r.T.max()]), # angle line on torque graph
    ]


STYLE = [ # look of each part in _frame, same order; set once, frames only change x, y and text
    dict(mode="lines", fill="toself", fillcolor=CAM_FILL, line=dict(color=LINE, width=2)), # cam
    dict(mode="lines", line=dict(color=LINE, width=1, dash="dot")), # base circle
    dict(mode="lines", line=dict(color=LINE, width=1, dash="dashdot")), # follower line
    dict(mode="markers+text", text=["O"], textposition="bottom left", marker=dict(color=LINE, size=7)), # cam centre O
    dict(mode="lines", line=dict(color=ACCENT, width=2)), # 0 deg mark
    dict(mode="lines", line=dict(color=SPRING, width=2)), # spring
    dict(mode="lines", line=dict(color=PART, width=6)), # rod
    dict(mode="lines", line=dict(color=PART, width=4)), # seat
    dict(mode="lines", fill="toself", fillcolor="white", line=dict(color=PART, width=2)), # roller
    dict(mode="markers", marker=dict(color=PART, size=6)), # roller centre
    dict(mode="lines+markers", line=dict(color=ACCENT, width=1.5),
         marker=dict(symbol="line-ew", size=10, line=dict(width=2, color=ACCENT))), # lift dimension
    dict(mode="text", textposition="bottom right", textfont=dict(size=13, color=LINE)), # readout
    dict(mode="markers", marker=dict(color=LIFT_COL, size=10)), # lift dot
    dict(mode="lines", line=dict(color=ANGLE_LINE, width=1)), # lift angle line
    dict(mode="markers", marker=dict(color=TORQUE_COL, size=10)), # torque dot
    dict(mode="lines", line=dict(color=ANGLE_LINE, width=1)), # torque angle line
]
WHERE = [(1, 1)] * 12 + [(1, 2)] * 2 + [(2, 2)] * 2 # subplot of each part: drawing, lift graph, torque graph


def animated_fig(r, p):
    span, base, top, sw = _sizes(p)
    skip = dict(hoverinfo="skip", showlegend=False)
    fig = make_subplots(rows=2, cols=2, horizontal_spacing=0.08, vertical_spacing=0.14,
                        specs=[[{"rowspan": 2}, {}], [None, {}]])

    for tr, st, (row, col) in zip(_frame(r, p, 0), STYLE, WHERE): # parts redrawn every frame
        fig.add_trace(tr.update(**st, **skip), row, col)
    moving = list(range(len(fig.data))) # indices the frames update

    fig.add_trace(go.Scatter(x=[p.d - 1.6 * sw, p.d + 1.6 * sw], y=[top, top], mode="lines",
                             line=dict(color=LINE, width=5), **skip), 1, 1) # fixed plate
    fig.add_trace(go.Scatter(x=r.theta, y=r.lift, mode="lines", line=dict(color=LIFT_COL, width=2), **skip), 1, 2) # lift curve
    fig.add_trace(go.Scatter(x=r.theta, y=r.T, mode="lines", line=dict(color=TORQUE_COL, width=2), **skip), 2, 2) # torque curve

    angles = np.arange(0, 360, FRAME_STEP)
    fig.frames = [go.Frame(name=f"{a:g}", data=_frame(r, p, a), traces=moving) for a in angles] # sent to the browser once

    play = dict(frame=dict(duration=40, redraw=True), transition=dict(duration=0), fromcurrent=True, mode="immediate")
    pause = dict(frame=dict(duration=0, redraw=False), mode="immediate")
    fig.update_layout(
        height=640, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white", paper_bgcolor="white",
        updatemenus=[dict(type="buttons", direction="left", x=0, y=-0.02, xanchor="left", yanchor="top",
                          buttons=[dict(label="Play", method="animate", args=[None, play]),
                                   dict(label="Pause", method="animate", args=[[None], pause])])],
        sliders=[dict(x=0.14, y=-0.02, len=0.86, xanchor="left", yanchor="top",
                      ticklen=0, font=dict(color="rgba(0,0,0,0)"), # hide the 180 step labels
                      currentvalue=dict(prefix="θ = ", suffix="°", font=dict(color=LINE)),
                      steps=[dict(label=f"{a:g}", method="animate",
                                  args=[[f"{a:g}"], dict(frame=dict(duration=0, redraw=True), mode="immediate")])
                             for a in angles])],
    )
    fig.update_xaxes(visible=False, range=[-span, span + abs(p.d) + 20], row=1, col=1)
    fig.update_yaxes(visible=False, range=[-span, top + 4], scaleanchor="x", scaleratio=1, row=1, col=1) # circles stay round
    for row, title in [(1, "lift (mm)"), (2, "torque (N·m)")]:
        fig.update_xaxes(range=[0, 360], dtick=60, gridcolor=GRID, row=row, col=2)
        fig.update_yaxes(title=title, gridcolor=GRID, zerolinecolor="#C9CFD2", row=row, col=2)
    fig.update_xaxes(title="cam angle (deg)", row=2, col=2)
    return fig