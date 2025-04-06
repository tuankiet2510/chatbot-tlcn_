Directory structure:
└── chatbot-tlcn/
    ├── README.md
    ├── alembic.ini
    ├── app.py
    ├── chainlit.md
    ├── db.py
    ├── docker-compose.yml
    ├── env.py
    ├── eval.ipynb
    ├── faq_evaluation_results.csv
    ├── faq_testset.csv
    ├── phone_evaluation_results.csv
    ├── phone_testset.csv
    ├── pyproject.toml
    ├── test.ipynb
    ├── test.py
    ├── .dockerignore
    ├── .env.example
    ├── .python-version
    ├── alembic/
    │   ├── README
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions/
    │       ├── 0113278eac18_modify_name_embedding_column_of_phones_.py
    │       ├── 0b47af67e745_edit_phone_table.py
    │       ├── 120a604fd902_add_vector_extension.py
    │       ├── 45d35c46a219_add_user_memory_table.py
    │       ├── 535089ddf724_add_contact_info_columns_into_user_.py
    │       ├── 672acb86aec9_create_faqs_table.py
    │       ├── 71321ac3cff1_add_embedding_column_for_phone_name_.py
    │       ├── 806ac93114b7_modify_brand_code_column_to_phones.py
    │       ├── 9e5da9e02a91_create_users_table.py
    │       ├── dc9bc54eaed6_create_phone_table.py
    │       ├── dd89958929b9_set_contraint_not_null_to_phone_table.py
    │       └── f4873b4eba7e_create_brand_table.py
    ├── chainlit_process/
    │   ├── authentication.py
    │   └── message.py
    ├── models/
    │   ├── base.py
    │   ├── brand.py
    │   ├── faq.py
    │   ├── message.py
    │   ├── phone.py
    │   ├── user.py
    │   └── user_memory.py
    ├── repositories/
    │   ├── brand.py
    │   ├── faq.py
    │   ├── phone.py
    │   ├── redis.py
    │   ├── user.py
    │   └── user_memory.py
    ├── service/
    │   ├── converter.py
    │   ├── email.py
    │   ├── embedding.py
    │   ├── openai.py
    │   └── store_chatbot.py
    ├── tasks/
    │   ├── faqs.csv
    │   ├── faqs.xlsx - Sheet1.csvZone.Identifier
    │   ├── import_brand_data.py
    │   ├── import_faq_data.py
    │   ├── import_phone_data.py
    │   ├── phone_data.jsonl
    │   ├── unique_brand_code.ipynb
    │   ├── unique_brands.json
    │   └── unique_product_types.json
    ├── tools/
    │   ├── collect_requirement.py
    │   ├── collect_user_contact_info.py
    │   ├── faq.py
    │   ├── invoke_tool.py
    │   ├── search_phone_database.py
    │   └── utils/
    │       ├── config.py
    │       └── search.py
    └── .chainlit/
        ├── config.toml
        └── translations/
            ├── bn.json
            ├── en-US.json
            ├── gu.json
            ├── he-IL.json
            ├── hi.json
            ├── kn.json
            ├── ml.json
            ├── mr.json
            ├── ta.json
            ├── te.json
            └── zh-CN.json
