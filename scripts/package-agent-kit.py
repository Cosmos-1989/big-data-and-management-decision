"""Package the editable teaching kit and keep the general code archive complete."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json

site = Path(__file__).resolve().parents[1]
root = site.parent
source = site / 'content-source/agent-course'
out = site / 'dist/downloads'
with ZipFile(out / 'enterprise-agent-kit.zip', 'w', ZIP_DEFLATED) as archive:
    for p in sorted((source / 'kit').rglob('*')):
        if p.is_file():
            archive.write(p, str(p.relative_to(source / 'kit')))
    archive.write(source / '14_ai_agent.md', 'docs/lecture_notes/14_ai_agent.md')
    archive.write(source / 'final_project.md', 'assignments/final_project.md')
    archive.write(source / 'cases.md', 'cases.md')
    archive.write(source / 'experiments.json', 'website/content-source/agent-course/experiments.json')
    for p in sorted((source / 'tests').glob('*.py')):
        archive.write(p, 'tests/' + p.name)
    # Minimal package hierarchy makes both portable tests executable after unzip.
    for relative in ['src/bdm_decision/__init__.py', 'src/bdm_decision/cases/__init__.py']:
        archive.write(root / relative, relative)
    archive.write(source / 'week14_enterprise_agents.py', 'src/bdm_decision/cases/week14_enterprise_agents.py')
    archive.write(root / 'LICENSE', 'LICENSE')
# Rebuild the existing archive from its entries, replacing the one new module.
p = out / 'course-code-data.zip'
with ZipFile(p) as archive:
    entries = {info.filename: archive.read(info) for info in archive.infolist()}
entries['src/bdm_decision/cases/week14_enterprise_agents.py'] = (source / 'week14_enterprise_agents.py').read_bytes()
with ZipFile(p, 'w', ZIP_DEFLATED) as archive:
    for name, contents in entries.items():
        archive.writestr(name, contents)
print(json.dumps({'kitBytes': (out / 'enterprise-agent-kit.zip').stat().st_size, 'generalArchiveHasAgentModule': True}))
