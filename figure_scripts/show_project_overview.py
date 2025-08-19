import pathlib

from prov.serializers.provrdf import ProvRDFSerializer
from prov.dot import prov_to_dot

with open("project_overview.ttl", encoding="utf-8") as f:
    doc = ProvRDFSerializer().deserialize(f)

dot_doc = prov_to_dot(doc, show_nary=False)
out_dir = (
    pathlib.Path(__file__)
    .resolve()
    .parents[1]
    .joinpath("figures", "show_project_overview")
)
out_dir.mkdir(parents=True, exist_ok=True)
dot_doc.write_png(out_dir.joinpath("project_overview.png"))
dot_doc.write_pdf(out_dir.joinpath("project_overview.pdf"))
dot_doc.write_svg(out_dir.joinpath("project_overview.svg"))
dot_doc.write_dot(out_dir.joinpath("project_overview.dot"))
