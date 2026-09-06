\set ON_ERROR_STOP on

BEGIN;

INSERT INTO users (id, email, display_name, created_at, updated_at)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'dev-user@example.com',
    'Dev User',
    '2026-09-06T00:00:00+00:00',
    '2026-09-06T00:00:00+00:00'
);

INSERT INTO workspaces (id, name, base_currency, created_at, updated_at)
VALUES (
    '10000000-0000-0000-0000-000000000001',
    'Household',
    'USD',
    '2026-09-06T00:00:00+00:00',
    '2026-09-06T00:00:00+00:00'
);

INSERT INTO categories (id, user_id, name, type, created_at, updated_at)
VALUES
    (
        '20000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000001',
        'Food',
        'expense',
        '2026-09-06T00:00:00+00:00',
        '2026-09-06T00:00:00+00:00'
    ),
    (
        '20000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000001',
        'Salary',
        'income',
        '2026-09-06T00:00:00+00:00',
        '2026-09-06T00:00:00+00:00'
    );

INSERT INTO workspace_members (workspace_id, user_id, role, created_at)
VALUES (
    '10000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000001',
    'owner',
    '2026-09-06T00:00:00+00:00'
);

INSERT INTO transactions (
    transaction_id,
    user_id,
    category_id,
    amount,
    currency,
    transaction_at,
    note,
    last_operation_key,
    version,
    deleted_at,
    created_at,
    updated_at
)
VALUES
    (
        '30000000-0000-0000-0000-000000000001',
        '00000000-0000-0000-0000-000000000001',
        '20000000-0000-0000-0000-000000000001',
        1200,
        'USD',
        1725580800123,
        'coffee',
        '1725580800123_seed_create_1',
        1,
        NULL,
        1725580800123,
        1725580800123
    ),
    (
        '30000000-0000-0000-0000-000000000002',
        '00000000-0000-0000-0000-000000000001',
        '20000000-0000-0000-0000-000000000002',
        500000,
        'USD',
        1725667200123,
        'salary',
        '1725667200123_seed_create_2',
        1,
        NULL,
        1725667200123,
        1725667200123
    ),
    (
        '30000000-0000-0000-0000-000000000003',
        '00000000-0000-0000-0000-000000000001',
        '20000000-0000-0000-0000-000000000001',
        2500,
        'USD',
        1725753600123,
        'deleted lunch',
        '1725753600123_seed_delete_1',
        2,
        1725757200123,
        1725753600123,
        1725757200123
    );

COMMIT;
