DROP TYPE institution_gender;
DROP TYPE institution_type;
CREATE TYPE institution_gender AS ENUM ('Boys', 'Girls', 'Co-ed');
CREATE TYPE institution_type AS ENUM ('Pre', 'Primary');