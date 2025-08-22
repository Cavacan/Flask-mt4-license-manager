from app import app, db, User, EA
from sqlalchemy.exc import IntegrityError

# アプリケーションコンテキストを確立
with app.app_context():
    print("データベースとテーブルを作成中...")
    db.create_all()
    print("データベースの作成が完了しました。")

    # 初期ユーザーの作成
    try:
        admin_username = 'admin'
        if not User.query.filter_by(username=admin_username).first():
            print(f"管理者ユーザー '{admin_username}' を作成中...")
            admin_user = User(username=admin_username, password='password', is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
            print(f"管理者ユーザー '{admin_username}' の作成が完了しました。")
        else:
            print(f"管理者ユーザー '{admin_username}' はすでに存在します。")

        # 初期EAの作成 (例)
        ea_name = 'ExampleEA'
        if not EA.query.filter_by(name=ea_name).first():
            print(f"初期EA '{ea_name}' を作成中...")
            example_ea = EA(name=ea_name)
            db.session.add(example_ea)
            db.session.commit()
            print(f"初期EA '{ea_name}' の作成が完了しました。")
        else:
            print(f"初期EA '{ea_name}' はすでに存在します。")

    except IntegrityError:
        db.session.rollback()
        print("初期データの作成中にエラーが発生しました。")
    except Exception as e:
        db.session.rollback()
        print(f"予期せぬエラーが発生しました: {e}")

print("初期化スクリプトの実行が完了しました。")