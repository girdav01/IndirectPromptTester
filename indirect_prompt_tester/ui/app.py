"""Streamlit UI application."""
import streamlit as st
from pathlib import Path
import pandas as pd
from typing import Optional

from ..generators import (
    ImageGenerator, DocumentGenerator, VideoGenerator,
    AudioGenerator, WebGenerator, SyslogGenerator
)
from ..distributors import (
    S3Distributor, EmailDistributor, SMSDistributor,
    WhatsAppDistributor, WebDistributor
)
from ..utils.config import Config
from ..utils.prompts import get_random_prompt, get_all_prompts
from ..sandbox.agent_runner import AgentRunner
from ..sandbox.monitor import SandboxMonitor

Config.ensure_directories()

st.set_page_config(
    page_title="Indirect Prompt Tester",
    page_icon="🔒",
    layout="wide"
)

def main():
    st.title("🔒 Indirect Prompt Tester Framework")
    st.markdown("Generate and test files with embedded indirect prompts")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["File Generator", "Distribution", "Sandbox", "Settings"]
    )
    
    if page == "File Generator":
        show_file_generator()
    elif page == "Distribution":
        show_distribution()
    elif page == "Sandbox":
        show_sandbox()
    elif page == "Settings":
        show_settings()

def show_file_generator():
    st.header("📄 File Generator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        file_type = st.selectbox(
            "File Type",
            ["image", "document", "video", "audio", "web", "syslog"]
        )
        
        prompt_source = st.radio(
            "Prompt Source",
            ["Custom", "Random", "Select from Examples"]
        )
        
        if prompt_source == "Custom":
            prompt = st.text_area("Enter your indirect prompt", height=100)
        elif prompt_source == "Random":
            prompt = get_random_prompt()
            st.text_area("Generated Prompt", prompt, height=100, disabled=True)
        else:
            example_prompts = get_all_prompts()
            selected_idx = st.selectbox(
                "Select Example Prompt",
                range(len(example_prompts)),
                format_func=lambda x: example_prompts[x][:50] + "..."
            )
            prompt = example_prompts[selected_idx]
            st.text_area("Selected Prompt", prompt, height=100, disabled=True)
    
    with col2:
        output_name = st.text_input("Output Filename", value="test_file")
        
        if file_type == "image":
            method = st.selectbox("Embedding Method", ["visible", "metadata", "steganography"])
            width = st.number_input("Width", min_value=100, max_value=4000, value=800)
            height = st.number_input("Height", min_value=100, max_value=4000, value=600)
        elif file_type == "document":
            doc_format = st.selectbox("Document Format", ["docx", "xlsx", "pptx", "pdf", "txt"])
            method = st.selectbox("Embedding Method", ["visible", "hidden", "metadata", "comments"])
        elif file_type == "video":
            method = st.selectbox("Embedding Method", ["visible", "metadata", "subtitles"])
            duration = st.number_input("Duration (seconds)", min_value=1, max_value=60, value=5)
        elif file_type == "audio":
            method = st.selectbox("Embedding Method", ["metadata", "steganography", "speech"])
            duration = st.number_input("Duration (seconds)", min_value=1, max_value=60, value=5)
        elif file_type == "web":
            method = st.selectbox("Embedding Method", ["visible", "hidden", "comments", "script", "meta"])
        elif file_type == "syslog":
            method = st.selectbox("Embedding Method", ["embedded", "hidden", "encoded"])
            num_entries = st.number_input("Number of Log Entries", min_value=10, max_value=1000, value=100)
    
    if st.button("Generate File", type="primary"):
        if not prompt:
            st.error("Please provide a prompt")
            return
        
        try:
            output_path = Config.GENERATED_FILES_DIR / output_name
            
            if file_type == "image":
                generator = ImageGenerator()
                generator.generate(prompt, output_path, method=method, width=width, height=height)
            elif file_type == "document":
                generator = DocumentGenerator()
                generator.generate(prompt, output_path, doc_type=doc_format, method=method)
            elif file_type == "video":
                generator = VideoGenerator()
                generator.generate(prompt, output_path, method=method, duration=duration)
            elif file_type == "audio":
                generator = AudioGenerator()
                generator.generate(prompt, output_path, method=method, duration=duration)
            elif file_type == "web":
                generator = WebGenerator()
                generator.generate(prompt, output_path, method=method)
            elif file_type == "syslog":
                generator = SyslogGenerator()
                generator.generate(prompt, output_path, method=method, num_entries=num_entries)
            
            st.success(f"✓ File generated: {output_path}")
            st.download_button(
                "Download File",
                data=output_path.read_bytes(),
                file_name=output_path.name,
                mime="application/octet-stream"
            )
            
            # Store in session state for distribution
            st.session_state['last_generated_file'] = str(output_path)
            st.session_state['last_prompt'] = prompt
        
        except Exception as e:
            st.error(f"Error generating file: {e}")

def show_distribution():
    st.header("📤 File Distribution")
    
    # Get file to distribute
    if 'last_generated_file' in st.session_state:
        default_file = st.session_state['last_generated_file']
    else:
        default_file = ""
    
    file_path = st.text_input("File Path", value=default_file)
    
    if not file_path or not Path(file_path).exists():
        st.warning("Please generate a file first or provide a valid file path")
        return
    
    distribution_method = st.selectbox(
        "Distribution Method",
        ["web", "s3", "email", "sms", "whatsapp"]
    )
    
    if distribution_method == "web":
        if st.button("Host File", type="primary"):
            try:
                distributor = WebDistributor()
                result = distributor.distribute(Path(file_path))
                if result.get('success'):
                    st.success(f"✓ File hosted at: {result['url']}")
                    st.code(result['url'])
            except Exception as e:
                st.error(f"Error: {e}")
    
    elif distribution_method == "s3":
        bucket = st.text_input("S3 Bucket (optional)", value=Config.AWS_S3_BUCKET)
        public = st.checkbox("Make Public")
        if st.button("Upload to S3", type="primary"):
            try:
                distributor = S3Distributor()
                result = distributor.distribute(Path(file_path), bucket=bucket, public=public)
                if result.get('success'):
                    st.success(f"✓ File uploaded to S3")
                    st.code(result['url'])
                else:
                    st.error(f"Error: {result.get('error')}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    elif distribution_method == "email":
        recipient = st.text_input("Recipient Email")
        subject = st.text_input("Subject (optional)")
        body = st.text_area("Body (optional)")
        if st.button("Send Email", type="primary"):
            try:
                distributor = EmailDistributor()
                result = distributor.distribute(Path(file_path), recipient=recipient, subject=subject, body=body)
                if result.get('success'):
                    st.success(f"✓ Email sent to {recipient}")
                else:
                    st.error(f"Error: {result.get('error')}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    elif distribution_method in ["sms", "whatsapp"]:
        recipient = st.text_input("Recipient Phone Number (E.164 format)")
        file_url = st.text_input("File URL (required)")
        message = st.text_area("Message (optional)")
        if st.button(f"Send via {distribution_method.upper()}", type="primary"):
            try:
                if distribution_method == "sms":
                    distributor = SMSDistributor()
                else:
                    distributor = WhatsAppDistributor()
                result = distributor.distribute(Path(file_path), recipient=recipient, file_url=file_url, message=message)
                if result.get('success'):
                    st.success(f"✓ Message sent to {recipient}")
                else:
                    st.error(f"Error: {result.get('error')}")
            except Exception as e:
                st.error(f"Error: {e}")

def show_sandbox():
    st.header("🧪 Sandbox Testing")
    
    runner = AgentRunner()
    monitor = SandboxMonitor()
    
    # File selection
    generated_files = list(Config.GENERATED_FILES_DIR.glob("*"))
    if not generated_files:
        st.warning("No generated files found. Generate a file first.")
        return
    
    selected_file = st.selectbox(
        "Select File to Test",
        generated_files,
        format_func=lambda x: x.name
    )
    
    # Agent selection
    agent_type = st.selectbox(
        "Agent Type",
        ["Local CLI", "OpenAI API", "Anthropic API", "Custom API"]
    )
    
    result = None
    
    if agent_type == "Local CLI":
        col1, col2 = st.columns(2)
        with col1:
            command = st.text_input("Command to run", value="python agent.py {file_path}")
        with col2:
            timeout = st.number_input("Timeout (seconds)", min_value=10, max_value=300, value=60)
        
        if st.button("Run Agent", type="primary"):
            with st.spinner("Running agent..."):
                result = runner.run_local_agent(command, selected_file, timeout=timeout)
    
    elif agent_type == "OpenAI API":
        col1, col2 = st.columns(2)
        with col1:
            api_key = st.text_input("OpenAI API Key", type="password")
        with col2:
            model = st.selectbox("Model", ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"])
        prompt = st.text_area("Optional Prompt", value="Process this file and tell me what you see.")
        
        if st.button("Test Agent", type="primary"):
            if not api_key:
                st.error("Please provide an API key")
            else:
                with st.spinner("Testing agent..."):
                    result = runner.run_openai_agent(selected_file, api_key, model=model, prompt=prompt)
    
    elif agent_type == "Anthropic API":
        col1, col2 = st.columns(2)
        with col1:
            api_key = st.text_input("Anthropic API Key", type="password")
        with col2:
            model = st.selectbox("Model", ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"])
        prompt = st.text_area("Optional Prompt", value="Process this file and tell me what you see.")
        
        if st.button("Test Agent", type="primary"):
            if not api_key:
                st.error("Please provide an API key")
            else:
                with st.spinner("Testing agent..."):
                    result = runner.run_anthropic_agent(selected_file, api_key, model=model, prompt=prompt)
    
    elif agent_type == "Custom API":
        col1, col2 = st.columns(2)
        with col1:
            endpoint = st.text_input("API Endpoint", value="https://api.example.com/process")
        with col2:
            api_key = st.text_input("API Key (optional)", type="password")
        method = st.selectbox("HTTP Method", ["POST", "GET"])
        
        if st.button("Test Agent", type="primary"):
            if not endpoint:
                st.error("Please provide an endpoint")
            else:
                with st.spinner("Testing agent..."):
                    result = runner.run_custom_api_agent(selected_file, endpoint, api_key=api_key, method=method)
    
    # Display results
    if result:
        st.subheader("Test Results")
        
        if result.get('success'):
            st.success("✓ Agent executed successfully")
        else:
            st.error("✗ Agent execution failed")
        
        # Analysis
        analysis = monitor.analyze_result(result)
        
        risk_color = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
        st.metric("Risk Level", f"{risk_color.get(analysis['risk_level'], '⚪')} {analysis['risk_level'].upper()}")
        
        if analysis['findings']:
            st.subheader("Findings")
            for finding in analysis['findings']:
                st.warning(finding)
        
        # Show response/output
        tabs = st.tabs(["Response", "Output", "Error", "Raw Result"])
        
        with tabs[0]:
            if result.get('response'):
                if isinstance(result['response'], dict):
                    st.json(result['response'])
                else:
                    st.text(result['response'])
            else:
                st.info("No response data")
        
        with tabs[1]:
            if result.get('output'):
                st.text(result['output'])
            else:
                st.info("No output")
        
        with tabs[2]:
            if result.get('error'):
                st.error(result['error'])
            else:
                st.info("No errors")
        
        with tabs[3]:
            st.json(result)
        
        # Save result
        if st.button("Save Result"):
            result_file = runner.save_result(result)
            st.success(f"Result saved to {result_file}")
    
    # Show previous results
    st.subheader("Previous Test Results")
    previous_results = runner.load_results()
    
    if previous_results:
        for prev_result in previous_results[:10]:  # Show last 10
            with st.expander(f"{Path(prev_result.get('file_path', 'unknown')).name} - {prev_result.get('timestamp', 'unknown')}"):
                prev_analysis = monitor.analyze_result(prev_result)
                st.write(f"**Agent:** {prev_result.get('agent_type', 'unknown')}")
                st.write(f"**Risk Level:** {prev_analysis['risk_level'].upper()}")
                st.write(f"**Success:** {prev_result.get('success', False)}")
                if st.button("View Details", key=f"view_{prev_result.get('timestamp', '')}"):
                    st.json(prev_result)
        
        if st.button("Generate Report"):
            report = monitor.generate_report(previous_results)
            report_path = monitor.save_report(report)
            st.success(f"Report generated: {report_path}")
            st.download_button(
                "Download Report",
                data=report,
                file_name=report_path.name,
                mime="text/plain"
            )
    else:
        st.info("No previous test results")

def show_settings():
    st.header("⚙️ Settings")
    
    st.subheader("Configuration Status")
    
    config_status = {
        "AWS S3": bool(Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY),
        "Twilio (SMS/WhatsApp)": bool(Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN),
        "Email (SMTP)": bool(Config.SMTP_USERNAME and Config.SMTP_PASSWORD),
    }
    
    for service, configured in config_status.items():
        status = "✓ Configured" if configured else "✗ Not Configured"
        st.write(f"{service}: {status}")
    
    st.info("Configure services by editing the .env file in the project root")

if __name__ == "__main__":
    main()

