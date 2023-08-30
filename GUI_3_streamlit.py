from streamlit.web import bootstrap

real_script = 'GUI_3.py'
bootstrap.run(real_script, f'run.py {real_script}', [], {})