import streamlit as st 
import openai
st.set_page_config(page_title="E-Waste Project", page_icon="🌍", layout="wide", initial_sidebar_state="expanded")
def chat_app(links,instance_key):
    # Initialize the session state if it doesn't exist for this instance
    if f'messages_{instance_key}' not in st.session_state:
        st.session_state[f'messages_{instance_key}'] = []

    # Placeholder for user chat input
    user_input = st.chat_input(placeholder='Your Message',key=str(instance_key))

    # Handle user input and get a response from the AI assistant
    if user_input:
        st.session_state[f'messages_{instance_key}'].append({"role": "user", "content": user_input})

        # Get response from OpenAI
        with st.spinner("AI is thinking..."):
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"""You are an AI assistant. 
                        Your job is to answer questions related to the given links.
                        Before answering, analyze the given links and provide information.
                        Links: {links}"""
                    },
                    {"role": "user", "content": user_input}
                ]
            )
            # Extract and display the assistant's response
            assistant_response = response.choices[0].message.content
            st.session_state[f'messages_{instance_key}'].append({"role": "assistant", "content": assistant_response})

    # Display previous chat messages from the session state
    for message in st.session_state[f'messages_{instance_key}']:
        with st.chat_message(message['role']):
            st.write(message['content'])


def main():
    E_Waste_Statistics = st.container(border=True)
    EU_Acts = st.container(border=True)
    with E_Waste_Statistics:
        c1,c2=st.columns([2.2,2])
        with c1:
            st.markdown("""

            ## E-Waste Statistics

            - In 2019, around 53.6Mt of WEEE was generated worldwide, with 12Mt assigned to the EU.
            - The secondary materials contained in this e-waste are estimated to be worth $57 billion.
            - Electronic Waste stocks are increasing at an alarming rate of 2MegaT per year.
            - It is projected that the global generation of WEEE will exceed 74Mt by 2030.5.
            - Only 17.4% of the global e-waste generated in 2019 was reported as collected and recycled by official WEEE management schemes.
            - In Europe, 42% of European WEEE is collected and recycled, with around one half in the EU.
            """)
        with c2:
            st.write("## E-Waste Projections")
            st.image(r'imgs_presentation/Statistics.png')
            st.image(r'imgs_presentation/projectoineWaste.png')
    with EU_Acts:
        st.write("## :flag-eu: Acts")
        with st.expander('Critical Raw Materials Act dd/mm/yyyy'):
            st.markdown("""
                - Critical Raw Materials Act Summary
                - Critical Materials
                https://single-market-economy.ec.europa.eu/sectors/raw-materials/areas-specific-interest/critical-raw-materials_en      
                - Link: https://single-market-economy.ec.europa.eu/sectors/raw-materials/areas-specific-interest/critical-raw-materials/critical-raw-materials-act_en
            """)
            links1=["https://single-market-economy.ec.europa.eu/sectors/raw-materials/areas-specific-interest/critical-raw-materials_en"]
            chat_app(links1,'CRM_ACT')

        with st.expander('Rare earth elements, permanent magnets, and motors'):
            st.markdown("""
                - Rare earth elements, permanent magnets, and motors
                https://single-market-economy.ec.europa.eu/sectors/raw-materials/areas-specific-interest/rare-earth-elements-permanent-magnets-and-motors_en
            """)
            links2=["https://single-market-economy.ec.europa.eu/sectors/raw-materials/areas-specific-interest/rare-earth-elements-permanent-magnets-and-motors_en"]
            chat_app(links2,'Rare earth elements')
        with st.expander('Restriction of Hazardous Substances in Electrical and Electronic Equipment (RoHS)'):
            st.markdown("""
                - Restriction of Hazardous Substances in Electrical and Electronic Equipment (RoHS)
                https://environment.ec.europa.eu/topics/waste-and-recycling/rohs-directive_en
            """)
            links3=["https://environment.ec.europa.eu/topics/waste-and-recycling/rohs-directive_en"]
            chat_app(links3,'HOS')

if __name__ == "__main__":
    main()