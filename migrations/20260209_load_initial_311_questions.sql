-- Migration: Load Initial Louisville 311 Approved Questions Corpus
-- Date: 2026-02-09
-- Purpose: Populate known Q&A pairs for B2C customer service chat
-- Source: Louisville Metro 311 common resident questions + system data

-- ============================================================================
-- GENERAL 311 SERVICE QUESTIONS
-- ============================================================================

INSERT INTO l311_approved_questions (
    question_text, answer_text, category, subcategory, question_type,
    keywords, common_variations, typical_urgency, service_name
) VALUES

-- What is 311?
('What is 311?',
'311 is Louisville Metro''s non-emergency service request system. It''s available 24/7 for reporting city service issues like potholes, missed trash pickup, code violations, park maintenance, and more. You can call 311 (or 574-5000 from outside Louisville), use the online portal at louisvilleky.gov/311, or download the mobile app. For emergencies, always call 911.',
'General', 'About 311', 'what_is',
ARRAY['what', '311', 'definition', 'about'],
ARRAY['What is Louisville 311?', 'Tell me about 311', 'What does 311 do?'],
'low', NULL),

-- How to submit
('How do I submit a 311 service request?',
'There are three easy ways to submit a 311 request: 1) Call 311 from within Louisville Metro (or 574-5000 from outside), 2) Visit the online portal at louisvilleky.gov/311, or 3) Download the Louisville Metro mobile app. When submitting, provide the location and a clear description of the issue. You''ll receive a tracking number to check the status of your request.',
'General', 'Submitting Requests', 'how_to',
ARRAY['submit', 'report', 'request', 'how'],
ARRAY['How can I report an issue?', 'How do I file a 311 request?', 'How to submit a service request?'],
'low', NULL),

-- Difference between 311 and 911
('What''s the difference between 311 and 911?',
'911 is for emergencies that require immediate police, fire, or medical response - like crimes in progress, fires, medical emergencies, or serious accidents. 311 is for non-emergency city services like reporting potholes, requesting bulk trash pickup, reporting code violations, or asking about city services. When in doubt: if it''s an emergency or someone''s safety is at risk, call 911.',
'General', 'About 311', 'what_is',
ARRAY['911', '311', 'difference', 'emergency'],
ARRAY['When do I call 311 vs 911?', '311 or 911?', 'Is this 311 or 911?'],
'low', NULL),

-- Tracking requests
('How do I track the status of my 311 request?',
'You can track your request using your tracking number in three ways: 1) Visit louisvilleky.gov/311 and enter your tracking number, 2) Call 311 and provide your tracking number, or 3) Use the mobile app to check status. If you don''t have your tracking number, call 311 with your address and request details - they can look it up for you.',
'General', 'Tracking', 'how_to',
ARRAY['track', 'status', 'check', 'follow up'],
ARRAY['Check my request status', 'Where is my 311 request?', 'How to check on my request?'],
'low', NULL),

-- Response times
('How long does it take to fix my issue?',
'Response times vary by issue type and urgency: High urgency issues (like water main breaks) are usually addressed within 24-48 hours. Standard requests (like pothole repairs) typically take 3-7 days. Routine maintenance can take 1-2 weeks depending on scheduling. You can call 311 anytime to check the status of your specific request using your tracking number.',
'General', 'Timelines', 'timeline',
ARRAY['how long', 'time', 'when', 'timeline'],
ARRAY['When will my issue be fixed?', 'How long will this take?', 'What''s the timeline?'],
'low', NULL);

-- ============================================================================
-- WASTE MANAGEMENT QUESTIONS
-- ============================================================================

INSERT INTO l311_approved_questions (
    question_text, answer_text, category, subcategory, question_type,
    keywords, common_variations, typical_urgency, typical_response_time, service_name
) VALUES

-- Bulk trash pickup
('How do I request bulk trash pickup?',
'To request bulk item pickup, call 311 with your address. Louisville Metro offers scheduled bulk pickup based on your neighborhood. Set items at the curb the night before your pickup day. Acceptable items include furniture, appliances, mattresses, and large household items. For faster service, you can also schedule pickup through the online portal at louisvilleky.gov/311 or the mobile app.',
'Waste Management', 'Bulk Pickup', 'how_to',
ARRAY['bulk', 'trash', 'pickup', 'furniture', 'large items'],
ARRAY['How to schedule bulk trash pickup?', 'Large item pickup', 'Furniture removal'],
'medium', '3-7 days', 'Large Item Appointment'),

-- Regular trash schedule
('When is my regular trash pickup day?',
'To find your specific trash pickup day, call 311 with your address or visit louisvilleky.gov/311 and enter your address. Regular trash pickup is weekly and varies by neighborhood. You can also download the Louisville Metro mobile app to see your collection schedule and set reminders.',
'Waste Management', 'Regular Collection', 'what_is',
ARRAY['trash', 'garbage', 'pickup', 'schedule', 'day'],
ARRAY['What day is trash pickup?', 'My garbage day', 'When do they collect trash?'],
'low', 'Immediate (information only)', 'Waste Management'),

-- Missed pickup
('My trash wasn''t picked up. What should I do?',
'If your trash was missed, call 311 to report it right away. Provide your address and the type of collection that was missed (regular trash, recycling, or yard waste). They''ll schedule a makeup pickup, usually within 24-48 hours. Make sure your bins were placed at the curb by 6 AM on your collection day and that items comply with collection guidelines.',
'Waste Management', 'Missed Pickup', 'how_to',
ARRAY['missed', 'trash', 'not picked up', 'forgot'],
ARRAY['They didn''t take my trash', 'Missed garbage pickup', 'Trash still at curb'],
'medium', '24-48 hours', 'Waste Management'),

-- Recycling questions
('What can I recycle?',
'Louisville Metro accepts paper, cardboard, plastic bottles (#1-7), aluminum and steel cans, and glass bottles and jars in your recycling bin. Do NOT include plastic bags, food waste, Styrofoam, or hazardous materials. For a complete list of acceptable items and recycling guidelines, visit louisvilleky.gov/government/solid-waste or call 311.',
'Waste Management', 'Recycling', 'what_is',
ARRAY['recycle', 'recycling', 'what', 'can'],
ARRAY['What goes in recycling?', 'Recyclable items', 'Can I recycle this?'],
'low', 'Immediate (information only)', 'Waste Management'),

-- Yard waste
('How do I dispose of yard waste?',
'Yard waste is collected weekly during the growing season (April-December) and biweekly in winter. Place leaves, grass clippings, and small branches in biodegradable paper bags or containers marked "Yard Waste." Branches must be bundled (under 4 feet long, under 2 inches diameter). For large amounts of yard waste, call 311 to arrange special pickup or visit a drop-off center.',
'Waste Management', 'Yard Waste', 'how_to',
ARRAY['yard waste', 'leaves', 'grass', 'branches'],
ARRAY['Leaf pickup', 'Grass clippings disposal', 'How to get rid of branches'],
'low', '1 week', 'Waste Management');

-- ============================================================================
-- STREET MAINTENANCE QUESTIONS
-- ============================================================================

INSERT INTO l311_approved_questions (
    question_text, answer_text, category, subcategory, question_type,
    keywords, common_variations, typical_urgency, typical_response_time, service_name
) VALUES

-- Pothole reporting
('How do I report a pothole?',
'To report a pothole, call 311 or submit online at louisvilleky.gov/311 with the exact location (address or cross streets). Describe the size and location in the road. You''ll get a tracking number to follow up. Pothole repairs typically take 3-7 days depending on severity and weather. For urgent safety hazards, mention that when reporting.',
'Street Maintenance', 'Pothole Repair', 'how_to',
ARRAY['pothole', 'report', 'road', 'street'],
ARRAY['Report a pothole', 'Fix pothole', 'Hole in road'],
'medium', '3-7 days', 'Street Maintenance'),

-- Streetlight out
('How do I report a streetlight that''s out?',
'To report a streetlight outage, call 311 or submit online with the nearest address or intersection. If possible, note the pole number (on a sticker on the pole). LG&E handles streetlight repairs, and Louisville Metro will forward your request. Repairs typically take 3-5 business days. For multiple lights out in an area, report all locations.',
'Street Maintenance', 'Streetlight', 'how_to',
ARRAY['streetlight', 'light', 'out', 'broken'],
ARRAY['Street light not working', 'Report broken streetlight', 'Light pole out'],
'low', '3-5 business days', 'Street Maintenance'),

-- Sidewalk repair
('How do I report damaged sidewalk?',
'To report sidewalk damage, call 311 with the location and description of the damage (cracked, uneven, missing sections). Louisville Metro Public Works will assess the sidewalk. Repair timeline varies based on severity and budget availability. For immediate safety hazards (large holes, completely missing sections), mention this when reporting for priority attention.',
'Street Maintenance', 'Sidewalk Repair', 'how_to',
ARRAY['sidewalk', 'damaged', 'broken', 'cracked'],
ARRAY['Broken sidewalk', 'Sidewalk needs repair', 'Cracked sidewalk'],
'medium', '2-4 weeks', 'Street Maintenance'),

-- Street sign issues
('How do I report a missing or damaged street sign?',
'Call 311 to report missing, damaged, or faded street signs. Provide the location (intersection or address) and describe the issue. Louisville Metro will replace or repair traffic and street name signs. Standard repairs take 5-7 business days. Stop signs and critical traffic signs are prioritized and typically replaced within 24-48 hours.',
'Street Maintenance', 'Street Signs', 'how_to',
ARRAY['sign', 'street sign', 'missing', 'damaged'],
ARRAY['Missing street sign', 'Broken sign', 'Faded sign'],
'medium', '5-7 days (24-48 hours for stop signs)', 'Street Maintenance');

-- ============================================================================
-- CODE ENFORCEMENT QUESTIONS
-- ============================================================================

INSERT INTO l311_approved_questions (
    question_text, answer_text, category, subcategory, question_type,
    keywords, common_variations, typical_urgency, typical_response_time, service_name
) VALUES

-- Property violations
('How do I report a property code violation?',
'Call 311 or submit online at louisvilleky.gov/311 to report property code violations like overgrown grass, abandoned vehicles, trash accumulation, or structural issues. Provide the address and describe the violation. Code Enforcement will inspect and contact the property owner if violations exist. Resolution timelines vary but inspections typically occur within 3-5 business days.',
'Code Enforcement', 'Property Violations', 'how_to',
ARRAY['code violation', 'property', 'report', 'complaint'],
ARRAY['Report code violation', 'Property complaint', 'Neighborhood violation'],
'low', '3-5 days for inspection', 'Code Enforcement'),

-- Abandoned vehicles
('How do I report an abandoned vehicle?',
'To report an abandoned vehicle on public property, call 311 with the location, vehicle description (make, model, color), and license plate if visible. The vehicle will be tagged and given time to be moved. If not moved within the specified time, it will be towed. For vehicles on private property, contact Code Enforcement through 311.',
'Code Enforcement', 'Abandoned Vehicles', 'how_to',
ARRAY['abandoned', 'vehicle', 'car', 'report'],
ARRAY['Report abandoned car', 'Junk car', 'Old vehicle on street'],
'low', '72 hours before tow', 'Code Enforcement'),

-- Tall grass
('How do I report overgrown grass or weeds?',
'Call 311 to report overgrown grass or weeds on a property. Provide the address. Code Enforcement will send a notice to the property owner to cut the grass within a specified timeframe (usually 10 days). If not addressed, the city may cut it and bill the owner. Grass must be kept under 12 inches tall within the city.',
'Code Enforcement', 'Tall Grass', 'how_to',
ARRAY['grass', 'overgrown', 'tall', 'weeds'],
ARRAY['Tall grass complaint', 'Overgrown lawn', 'Weed complaint'],
'low', '10 days for compliance', 'Code Enforcement');

-- ============================================================================
-- PARKS AND RECREATION QUESTIONS
-- ============================================================================

INSERT INTO l311_approved_questions (
    question_text, answer_text, category, subcategory, question_type,
    keywords, common_variations, typical_urgency, typical_response_time, service_name
) VALUES

-- Park maintenance
('How do I report a problem at a park?',
'Call 311 to report park issues like broken equipment, maintenance needs, lighting problems, or safety concerns. Provide the park name and location of the issue. Louisville Metro Parks will assess and prioritize repairs. Urgent safety issues (broken glass, dangerous equipment) are addressed within 24-48 hours. Routine maintenance may take 1-2 weeks.',
'Parks', 'Park Maintenance', 'how_to',
ARRAY['park', 'playground', 'broken', 'equipment'],
ARRAY['Report park problem', 'Broken playground equipment', 'Park needs repair'],
'medium', '24-48 hours (urgent), 1-2 weeks (routine)', 'Parks'),

-- Tree issues
('How do I report a tree problem?',
'To report tree issues on public property (fallen trees, dead trees, hanging branches), call 311 with the location. Louisville Metro Forestry will assess the tree. Emergency situations (trees blocking roads, immediate hazards) are handled within 24 hours. Non-emergency tree trimming and removal can take 2-4 weeks. For trees on private property, contact a private tree service.',
'Parks', 'Tree Maintenance', 'how_to',
ARRAY['tree', 'fallen', 'dead', 'branches'],
ARRAY['Report fallen tree', 'Dead tree', 'Tree hanging over road'],
'medium', '24 hours (emergency), 2-4 weeks (routine)', 'Parks');

-- ============================================================================
-- ANIMAL CONTROL QUESTIONS
-- ============================================================================

INSERT INTO l311_approved_questions (
    question_text, answer_text, category, subcategory, question_type,
    keywords, common_variations, typical_urgency, typical_response_time, service_name
) VALUES

-- Stray animals
('How do I report a stray animal?',
'For stray animals, call Louisville Metro Animal Services directly at (502) 473-PETS (7387) or 311. Provide the location and description of the animal. If the animal appears aggressive or injured, mention this for priority response. Animal Services will dispatch an officer. Response times vary based on urgency and current call volume. For aggressive or dangerous animals, call 911 if there''s an immediate threat.',
'Animal Control', 'Stray Animals', 'how_to',
ARRAY['stray', 'animal', 'dog', 'cat'],
ARRAY['Report stray dog', 'Stray animal', 'Lost pet'],
'medium', 'Varies by urgency', 'Animal Control'),

-- Barking dogs
('How do I report a barking dog complaint?',
'For ongoing barking dog complaints, call 311. Provide the address where the dog is located and details about when the barking occurs. Louisville Metro will send a notice to the property owner. Keep a log of dates and times if the issue continues. For immediate disturbances late at night, you can also contact LMPD non-emergency at (502) 574-7111.',
'Animal Control', 'Noise Complaints', 'how_to',
ARRAY['barking', 'dog', 'noise', 'complaint'],
ARRAY['Neighbor''s dog barking', 'Dog noise complaint', 'Barking dog'],
'low', '3-5 days for notice', 'Animal Control');

-- ============================================================================
-- WATER/SEWER QUESTIONS
-- ============================================================================

INSERT INTO l311_approved_questions (
    question_text, answer_text, category, subcategory, question_type,
    keywords, common_variations, typical_urgency, typical_response_time, service_name
) VALUES

-- Water main break
('How do I report a water main break?',
'Water main breaks are emergencies. Call 311 immediately or Louisville Water Company''s emergency line at (502) 583-6610 (available 24/7). Provide the location and describe what you see (water gushing, flooding). Water main breaks are prioritized and crews are typically dispatched within 1-2 hours. For severe flooding that threatens property, also call 911.',
'Water/Sewer', 'Water Main', 'how_to',
ARRAY['water', 'main break', 'leak', 'flooding'],
ARRAY['Water main break', 'Water leak', 'Water flooding street'],
'high', '1-2 hours', 'Water Emergency'),

-- Sewer backup
('How do I report a sewer backup?',
'For sewer backups in the street or public areas, call 311 or Louisville MSD''s emergency line at (502) 540-6000. For backups in your home, first check if it''s a private line issue (contact a plumber). If you believe it''s the public sewer, call MSD. Provide the location and description. Public sewer emergencies are addressed within 2-4 hours. Keep children and pets away from the area.',
'Water/Sewer', 'Sewer', 'how_to',
ARRAY['sewer', 'backup', 'overflow', 'manhole'],
ARRAY['Sewer backup', 'Sewer overflow', 'Manhole overflowing'],
'high', '2-4 hours', 'Sewer Emergency');

-- ============================================================================
-- VERIFY INSERTION
-- ============================================================================
DO $$
DECLARE
    question_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO question_count FROM l311_approved_questions;
    RAISE NOTICE 'Total questions loaded into Louisville 311 corpus: %', question_count;
END $$;

-- Display category breakdown
SELECT
    category,
    COUNT(*) as question_count,
    string_agg(DISTINCT question_type, ', ' ORDER BY question_type) as question_types
FROM l311_approved_questions
GROUP BY category
ORDER BY question_count DESC;
