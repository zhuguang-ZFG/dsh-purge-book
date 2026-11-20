// Convert authored centerlines into portable filled SVG outlines at build time.
// perfect-freehand is an MIT dependency; see VISUAL_REFERENCES.md.
import { getStroke } from 'perfect-freehand';

let input = '';
for await (const chunk of process.stdin) input += chunk;
const strokes = JSON.parse(input);
const number = value => Number(value.toFixed(2));
const midpoint = (a, b) => [number((a[0] + b[0]) / 2), number((a[1] + b[1]) / 2)];

const paths = strokes.map(({ points, width, closed }) => {
  if (points.length < 2 || !Number.isFinite(width) || width <= 0 ||
      points.some(p => p.length !== 3 || p.some(n => !Number.isFinite(n)))) {
    throw new Error('Invalid pen geometry');
  }
  const outline = getStroke(points, {
    size: width, thinning: 0.5, smoothing: 0.35, streamline: 0,
    simulatePressure: false, last: true,
    start: { taper: closed ? 0 : width * 1.5 },
    end: { taper: closed ? 0 : width * 2.5 },
  });
  if (outline.length < 3) throw new Error('Empty pen outline');
  // Quadratic arcs through edge midpoints keep the polygon smooth and closed.
  let path = `M${midpoint(outline.at(-1), outline[0]).join(' ')}`;
  outline.forEach((p, i) => {
    const end = midpoint(p, outline[(i + 1) % outline.length]);
    path += `Q${number(p[0])} ${number(p[1])} ${end.join(' ')}`;
  });
  return path + 'Z';
});
process.stdout.write(JSON.stringify(paths));
