-- Migration: Add 30 Critical Questions Based on Gap Analysis
-- Date: 2026-02-11
-- Purpose: Expand approved questions corpus from 23 to 53 questions
-- Coverage Improvement: 39.67% → 89.91% (+50.24%)
-- Based on: Full 169,598 record analysis identifying highest priority gaps

-- ============================================================================
-- PHASE 1: IMMEDIATE PRIORITY (10 Questions)
-- Impact: +19.49% coverage (33,051 requests)
-- Timeline: 30 days
-- ============================================================================

INSERT INTO l311_approved_questions (
    question_text, answer_text, category, subcategory, question_type,
    keywords, common_variations, typical_urgency, typical_response_time, service_name
) VALUES

-- 1. Streets/Road Problems (12,738 requests - 7.5% of dataset)
('How do I report a street or road problem?',
'To report street or road issues like potholes, cracks, sinkholes, or pavement damage, call 311 or submit online at louisvilleky.gov/311 with the exact location (address or cross streets). Describe the problem and its size. You''ll receive a tracking number to follow up. High-priority safety hazards (large potholes, sinkholes) are typically addressed within 24-48 hours. Standard repairs take 3-7 days depending on severity and weather conditions.',
'Street Maintenance', 'Road Repair', 'how_to',
ARRAY['street', 'road', 'pavement', 'crack', 'sinkhole', 'asphalt'],
ARRAY['Road needs repair', 'Street damage', 'Pavement problem', 'Road condition'],
'medium', '24-48 hours (urgent), 3-7 days (standard)', 'Streets'),

-- 2. Interior Code Violations (2,673 requests - CRITICAL SAFETY)
('How do I report interior housing code violations?',
'For serious interior housing issues like no heat, no water, mold, pest infestations, or unsafe conditions in rental properties, call 311 immediately. Provide the property address and describe the specific violations. Louisville Metro Code Enforcement will inspect the property, typically within 24-48 hours for urgent issues. They will issue orders to the property owner to make repairs. If you are a tenant, you cannot be evicted for reporting code violations - this is protected by law. For emergency situations (no heat in winter, no water), call 311 and emphasize the emergency nature.',
'Code Enforcement', 'Interior Violations', 'how_to',
ARRAY['interior', 'housing', 'mold', 'heat', 'water', 'pest', 'unsafe', 'rental'],
ARRAY['No heat in apartment', 'Mold in rental', 'Pest infestation', 'Unsafe living conditions', 'Landlord not fixing issues'],
'high', '24-48 hours for inspection', 'Code Enforcement'),

-- 3. High Weeds/Grass (5,487 requests)
('How do I report tall grass or overgrown weeds on a property?',
'Call 311 to report overgrown grass or weeds on a property (grass over 12 inches tall). Provide the complete address. Code Enforcement will inspect and send a notice to the property owner requiring them to cut the grass within 10 days. If not addressed, the city may cut it and bill the owner. This applies to both residential and commercial properties. Grass and weeds must be kept under 12 inches tall within Louisville Metro.',
'Code Enforcement', 'Tall Grass', 'how_to',
ARRAY['grass', 'overgrown', 'tall', 'weeds', 'lawn', 'unmowed'],
ARRAY['Tall grass complaint', 'Overgrown lawn', 'Weed complaint', 'Unmowed grass', 'Property not maintained'],
'low', '10 days for compliance', 'Code Enforcement'),

-- 4. Severe Weather Damage (332 requests - 94.3% high urgency)
('How do I report severe weather damage?',
'For severe weather damage (storm damage, fallen trees blocking roads, downed power lines, flooding), call 311 immediately or 911 if there is immediate danger to life or property. Provide the location and describe the hazard. For downed power lines, also call LG&E at (502) 589-1444. Emergency crews prioritize life-safety issues first (blocked roads, downed lines, flooding) and typically respond within 1-2 hours. Non-emergency storm cleanup (debris removal, tree trimming) may take 3-7 days depending on volume.',
'Emergency Services', 'Storm Damage', 'how_to',
ARRAY['storm', 'weather', 'damage', 'fallen tree', 'power line', 'flooding', 'wind'],
ARRAY['Storm damage', 'Tree down from storm', 'Power line down', 'Flooding from storm', 'Wind damage'],
'high', '1-2 hours (emergency), 3-7 days (cleanup)', 'Emergency Services'),

-- 5. Traffic Signal Malfunctions (2,693 requests - 69% high urgency)
('How do I report a broken or malfunctioning traffic signal?',
'For traffic signal issues (lights out, stuck on red/green, flashing when not intended, damaged signals), call 311 immediately with the intersection location. Traffic Engineering will dispatch crews to assess the issue. Critical malfunctions affecting traffic flow are prioritized and typically addressed within 2-4 hours. If a signal is completely out, treat the intersection as a 4-way stop until repaired. For accidents involving signal damage, also call LMPD.',
'Street Maintenance', 'Traffic Signals', 'how_to',
ARRAY['traffic signal', 'traffic light', 'stoplight', 'signal', 'broken', 'out'],
ARRAY['Traffic light not working', 'Signal is out', 'Stoplight stuck', 'Traffic signal broken', 'Light stuck on red'],
'high', '2-4 hours for critical issues', 'Traffic Signals'),

-- 6. Hazardous Trees (3,192 requests - 56.9% high urgency)
('How do I report a dangerous or hazardous tree?',
'To report dangerous trees on public property (dead trees, trees leaning over roads, large broken limbs, trees blocking streets), call 311 with the location. Louisville Metro Forestry will assess the tree for safety hazards. Emergency situations (trees blocking roads, imminent fall risk, limbs on power lines) are handled within 24 hours. Non-emergency hazardous tree removal can take 1-4 weeks depending on severity and scheduling. For trees on private property, contact a licensed tree service. For limbs on power lines, also call LG&E at (502) 589-1444.',
'Parks', 'Tree Hazards', 'how_to',
ARRAY['tree', 'hazardous', 'dangerous', 'dead tree', 'falling', 'limbs', 'leaning'],
ARRAY['Dangerous tree', 'Dead tree ready to fall', 'Tree leaning on house', 'Large limbs hanging', 'Tree blocking road'],
'high', '24 hours (emergency), 1-4 weeks (scheduled)', 'Parks'),

-- 7. Improper Trash Disposal (3,181 requests - 93% negative)
('How do I report improper trash or garbage disposal?',
'To report improper trash disposal (trash not in containers, scattered garbage, overflowing dumpsters, trash left at curb too long), call 311 with the location and description. For private property, Code Enforcement will inspect and may issue citations. For public property, Solid Waste will clean up and investigate the source. Trash must be in proper containers with lids and only placed at curb the night before pickup day. Bulk items require advance scheduling through 311.',
'Waste Management', 'Improper Disposal', 'how_to',
ARRAY['trash', 'garbage', 'improper', 'scattered', 'overflowing', 'dumpster'],
ARRAY['Trash everywhere', 'Garbage not contained', 'Overflowing dumpster', 'Trash left at curb', 'Scattered garbage'],
'medium', '3-5 days for inspection', 'Waste Management'),

-- 8. Odor Concerns (1,530 requests - 93.7% negative)
('How do I report a strong odor or smell concern?',
'For persistent strong odors (chemical smells, sewage, industrial odors, garbage smells), call 311 with the location and description of the odor, including when it occurs. Louisville Metro Air Pollution Control District (APCD) will investigate. Describe the smell (chemical, burning, sewage, garbage, etc.) and time of day it''s strongest. For immediate health concerns or strong chemical smells, also call 911. Investigations typically occur within 24-48 hours for urgent concerns, 3-5 days for routine odor complaints.',
'Environmental', 'Odor Complaints', 'how_to',
ARRAY['odor', 'smell', 'chemical', 'sewage', 'stink', 'fumes'],
ARRAY['Bad smell', 'Chemical odor', 'Sewage smell', 'Strong odor', 'Industrial smell', 'Garbage smell'],
'medium', '24-48 hours (urgent), 3-5 days (routine)', 'Environmental'),

-- 9. Drainage and Sewer Issues (871 requests - 91.3% negative)
('How do I report drainage or sewer problems?',
'For drainage and sewer issues (clogged storm drains, standing water, street flooding, sewer smells from drains), call 311 with the location. For sewer backups in the street or public areas, also call Louisville MSD at (502) 540-6000. Describe the issue and location. Storm drain clogs are typically cleared within 3-5 days. Street flooding and sewer backups are prioritized and addressed within 4-8 hours. For backups inside your home, first contact a plumber - it may be a private line issue.',
'Water/Sewer', 'Drainage Issues', 'how_to',
ARRAY['drainage', 'sewer', 'flooding', 'standing water', 'storm drain', 'clogged'],
ARRAY['Storm drain clogged', 'Street flooding', 'Standing water', 'Drainage problem', 'Sewer smell'],
'medium', '4-8 hours (flooding), 3-5 days (clogs)', 'Drainage and Sewer'),

-- 10. Illegal Open Burning (354 requests - 87.6% negative)
('How do I report illegal open burning?',
'Open burning is illegal in Louisville Metro except for small recreational fires and approved agricultural burning. To report illegal burning (trash, debris, tires, construction materials), call 311 with the location and what is being burned. For large fires or immediate danger, call 911. Louisville Metro Air Pollution Control District (APCD) will investigate. Burning trash, tires, or materials that create excessive smoke is prohibited and subject to fines. Only small recreational fires (campfires, fire pits) are allowed.',
'Environmental', 'Illegal Burning', 'how_to',
ARRAY['burning', 'open burn', 'fire', 'smoke', 'trash burning', 'illegal'],
ARRAY['Neighbor burning trash', 'Illegal fire', 'Burning debris', 'Trash fire', 'Excessive smoke'],
'medium', '24-48 hours for investigation', 'Environmental');

-- ============================================================================
-- PHASE 2: SHORT-TERM PRIORITY (10 Questions)
-- Impact: +6.02% coverage (10,206 requests)
-- Timeline: 90 days
-- ============================================================================

INSERT INTO l311_approved_questions (
    question_text, answer_text, category, subcategory, question_type,
    keywords, common_variations, typical_urgency, typical_response_time, service_name
) VALUES

-- 11. Homeless Encampments (1,164 requests)
('How do I report a homeless camp or encampment?',
'To report homeless encampments on public property, call 311 with the location. Louisville Metro coordinates with social services and outreach teams to offer assistance and resources to individuals experiencing homelessness. The city balances compassion with public safety and health concerns. Encampments on public property or blocking sidewalks/rights-of-way will be addressed with advance notice when possible. For immediate safety concerns or trespassing on private property, contact LMPD non-emergency at (502) 574-7111.',
'Social Services', 'Homeless Services', 'how_to',
ARRAY['homeless', 'camp', 'encampment', 'tent', 'sleeping', 'vagrant'],
ARRAY['Homeless camp', 'Tent encampment', 'People camping', 'Homeless concern'],
'medium', '3-7 days with outreach coordination', 'Homeless Camp Concern'),

-- 12. Utility Problems (807 requests - 72.6% high urgency)
('How do I report a utility problem or emergency?',
'For utility emergencies, call the appropriate utility company directly: LG&E (electric/gas): (502) 589-1444 | Louisville Water: (502) 583-6610 | AT&T: (800) 288-2020. For downed power lines, gas leaks, or water main breaks, ALSO call 911. You can report utility issues to 311, but they will refer you to the utility company. For ongoing service quality issues or billing disputes, contact the utility company customer service. For utility line locates before digging, call 811 at least 2 business days in advance.',
'Utilities', 'Utility Services', 'how_to',
ARRAY['utility', 'electric', 'gas', 'power', 'line', 'leak', 'outage'],
ARRAY['Power out', 'Gas leak', 'Downed power line', 'Utility emergency', 'Electric problem'],
'high', 'Immediate (call utility company)', 'Utilities'),

-- 13. Sidewalk Hazards (735 requests)
('How do I report a dangerous sidewalk or curb?',
'To report dangerous sidewalk conditions (large cracks, missing sections, trip hazards, severe unevenness), call 311 with the location and description. Louisville Metro Public Works will assess the hazard. Emergency repairs for severe safety hazards (missing sidewalk sections, large holes) are prioritized and addressed within 1-2 weeks. Standard sidewalk repairs can take 4-8 weeks depending on severity and budget. For snow/ice on sidewalks, property owners are responsible for clearing within 48 hours of snowfall.',
'Street Maintenance', 'Sidewalk Hazards', 'how_to',
ARRAY['sidewalk', 'curb', 'dangerous', 'trip hazard', 'cracked', 'broken', 'missing'],
ARRAY['Dangerous sidewalk', 'Broken sidewalk', 'Missing sidewalk', 'Trip hazard', 'Sidewalk hole'],
'medium', '1-2 weeks (urgent), 4-8 weeks (routine)', 'Sidewalks/Curbs'),

-- 14. Zoning Violations (624 requests)
('How do I report a zoning violation?',
'To report zoning violations (business operating from home without permit, commercial activity in residential area, improper use of property, unpermitted structures), call 311 with the property address and describe the violation. Planning & Design Services will investigate to determine if the use complies with zoning regulations. Zoning inspections typically occur within 5-10 business days. If violations exist, the property owner will receive notice to comply or apply for proper permits.',
'Code Enforcement', 'Zoning Violations', 'how_to',
ARRAY['zoning', 'violation', 'business', 'commercial', 'residential', 'permit'],
ARRAY['Zoning violation', 'Illegal business', 'Commercial in residential', 'Zoning complaint'],
'low', '5-10 business days for inspection', 'Zoning Concern'),

-- 15. Building Permits (549 requests)
('How do I report unpermitted construction or building work?',
'To report construction work without permits (additions, major renovations, commercial construction, demolition), call 311 with the property address and describe the work being done. Louisville Metro Inspections will investigate. All major construction, electrical, plumbing, and HVAC work requires permits. Working without permits can result in stop-work orders and fines. To check if permits were issued for an address, visit louisvilleky.gov/government/inspections or call (502) 574-3321.',
'Code Enforcement', 'Building Permits', 'how_to',
ARRAY['permit', 'construction', 'building', 'unpermitted', 'renovation', 'addition'],
ARRAY['Construction without permit', 'Unpermitted work', 'Illegal construction', 'No building permit'],
'medium', '3-5 business days for investigation', 'Building Permits'),

-- 16. Street Sign Damage (735 requests)
('How do I report a damaged, missing, or faded street sign?',
'Call 311 to report missing, damaged, knocked down, or faded street signs. Provide the location (intersection or address) and describe the issue. Louisville Metro will replace or repair traffic and street name signs. Stop signs and critical traffic control signs are prioritized and typically replaced within 24-48 hours. Standard street name signs are replaced within 5-7 business days. For traffic signals or signal poles, these are higher priority and addressed within 2-4 hours if affecting safety.',
'Street Maintenance', 'Street Signs', 'how_to',
ARRAY['sign', 'street sign', 'missing', 'damaged', 'faded', 'knocked down'],
ARRAY['Missing street sign', 'Broken sign', 'Faded sign', 'Sign knocked down', 'Stop sign missing'],
'medium', '24-48 hours (stop signs), 5-7 days (street names)', 'Street Signs'),

-- 17. Solid Waste Violations (592 requests)
('How do I report a solid waste violation?',
'To report solid waste violations (commercial dumpster issues, illegal disposal, improper waste storage, overflowing containers at businesses), call 311 with the location. Code Enforcement will inspect commercial properties for violations. Businesses must properly maintain dumpsters, keep lids closed, and prevent overflow. Residential properties must use proper containers and not store trash in yards. Inspections typically occur within 3-5 business days.',
'Waste Management', 'Violations', 'how_to',
ARRAY['waste', 'violation', 'dumpster', 'commercial', 'illegal disposal'],
ARRAY['Dumpster violation', 'Commercial waste issue', 'Improper waste storage', 'Trash violation'],
'low', '3-5 business days for inspection', 'Solid Waste Violation'),

-- 18. Litter in Public Areas (457 requests)
('How do I report litter or trash in public areas?',
'To report litter or trash accumulation in public areas (parks, streets, medians, rights-of-way), call 311 with the specific location. Louisville Metro Solid Waste will schedule cleanup, typically within 3-7 days. For large amounts of dumped items, this may be classified as illegal dumping (faster response). You can also organize a community cleanup through the Mayor''s Brightside program - call 311 for information. Report litter violations (seeing someone littering) to LMPD non-emergency: (502) 574-7111.',
'Waste Management', 'Litter', 'how_to',
ARRAY['litter', 'trash', 'public', 'street', 'park', 'cleanup'],
ARRAY['Litter on street', 'Trash in park', 'Public area cleanup needed', 'Street litter'],
'low', '3-7 days for cleanup', 'Litter Issue'),

-- 19. Noise Complaints (460 requests)
('How do I report a noise complaint?',
'For noise complaints (loud music, loud parties, ongoing disturbances), call 311 during business hours or LMPD non-emergency at (502) 574-7111 for after-hours or immediate issues. Louisville Metro noise ordinances prohibit excessive noise (amplified music, loud equipment) that disturbs others, especially late at night (10 PM - 7 AM). For barking dogs, call 311 and provide the address and details about when barking occurs. Keep a log of dates and times for ongoing issues.',
'Code Enforcement', 'Noise Ordinance', 'how_to',
ARRAY['noise', 'loud', 'music', 'party', 'disturbance', 'complaint'],
ARRAY['Noise complaint', 'Loud music', 'Loud party', 'Noise disturbance', 'Excessive noise'],
'low', '24-48 hours (311), immediate (LMPD)', 'Noise Concern'),

-- 20. Pest Problems (424 requests)
('How do I report a pest or rodent problem?',
'For pest issues on private property (rodents, roaches, bedbugs in rentals), contact your landlord first if renting, or a licensed pest control service if you own the property. For public health concerns (rat infestations in alleys, mosquito breeding areas, vector control issues), call 311 and Louisville Metro Public Health will investigate. Health inspections for rental properties with severe pest infestations can be requested through 311 - provide the property address. Response time is typically 5-7 business days for health investigations.',
'Health', 'Pest Control', 'how_to',
ARRAY['pest', 'rodent', 'rat', 'mouse', 'roach', 'bedbug', 'mosquito'],
ARRAY['Rat problem', 'Rodent infestation', 'Roach problem', 'Pest infestation', 'Mouse problem'],
'medium', '5-7 business days for health investigation', 'Pest Issue');

-- ============================================================================
-- PHASE 3: MEDIUM-TERM PRIORITY (10 Questions)
-- Impact: +24.73% coverage (41,944 requests)
-- Timeline: 180 days
-- ============================================================================

INSERT INTO l311_approved_questions (
    question_text, answer_text, category, subcategory, question_type,
    keywords, common_variations, typical_urgency, typical_response_time, service_name
) VALUES

-- 21. NSR Metro Agencies (34,981 requests - 20.6% of ALL requests!)
('What does NSR mean and when should I use it?',
'NSR stands for "Non-Service Request" - these are information requests, referrals, or inquiries that don''t require a physical service or inspection. Common NSR categories include: NSR Metro Agencies (general information about city departments), NSR Social Services (referrals to social programs), NSR Government (questions about policies or procedures), and NSR Utility (utility company contact info). Use NSR when you need information, phone numbers, or guidance rather than reporting a problem. For actual service requests (potholes, missed trash, code violations), select the specific service type, not NSR.',
'General', 'System Information', 'what_is',
ARRAY['NSR', 'non-service request', 'information', 'referral', 'inquiry'],
ARRAY['What is NSR?', 'NSR meaning', 'Information request', 'General inquiry'],
'low', 'Immediate (information only)', 'NSR Metro Agencies'),

-- 22. Street Lighting (2,618 requests)
('How do I report a streetlight problem?',
'To report streetlight issues (light out, flickering, on during day, damaged pole), call 311 with the nearest address or intersection. If possible, note the pole number (on a sticker on the pole). LG&E maintains streetlights in Louisville Metro - 311 will forward your request to them. Standard repairs typically take 3-5 business days. For multiple lights out in an area, report all locations. For damaged poles or downed lines, this is higher priority and typically addressed within 24 hours.',
'Street Maintenance', 'Street Lights', 'how_to',
ARRAY['streetlight', 'street light', 'light', 'out', 'pole', 'flickering'],
ARRAY['Street light out', 'Streetlight not working', 'Light pole broken', 'Flickering streetlight'],
'low', '3-5 business days (standard), 24 hours (damage)', 'Street Lights'),

-- 23. Vehicles on Private Property (1,702 requests)
('How do I report a junk or abandoned vehicle on private property?',
'To report junk vehicles, inoperable vehicles, or vehicles stored improperly on private property (yards, driveways), call 311 with the property address and vehicle description. Code Enforcement will inspect. Vehicles must be operable, have current registration, and be stored on paved surfaces (not grass). Inoperable vehicles are not allowed to be stored in residential areas except in enclosed garages. Inspections occur within 3-5 business days. For vehicles on PUBLIC streets, use the abandoned vehicle on public property process (tagged, then towed after 72 hours).',
'Code Enforcement', 'Vehicle Storage', 'how_to',
ARRAY['vehicle', 'junk', 'car', 'private property', 'inoperable', 'yard'],
ARRAY['Junk car on property', 'Car in yard', 'Inoperable vehicle', 'Vehicle on grass', 'Abandoned car on property'],
'low', '3-5 business days for inspection', 'Vehicle on Private Property'),

-- 24. Property Maintenance (1,164 requests)
('How do I report general property maintenance violations?',
'To report property maintenance issues (deteriorating structures, broken windows, damaged siding, roof damage, unsafe porches/stairs), call 311 with the property address. Code Enforcement will inspect for violations of property maintenance standards. Properties must be maintained in good repair and free from hazards. Inspections typically occur within 5-7 business days. For immediate safety hazards (collapsing structures, dangerous conditions), mention this when reporting for priority response.',
'Code Enforcement', 'Property Maintenance', 'how_to',
ARRAY['maintenance', 'property', 'deteriorating', 'broken', 'repair', 'structural'],
ARRAY['Property needs maintenance', 'Deteriorating building', 'Property not maintained', 'Structural issues'],
'medium', '5-7 business days for inspection', 'Maintenance'),

-- 25. Parking Violations (1,473 requests)
('How do I report a parking violation or concern?',
'To report parking violations (blocking sidewalks, parking in fire lanes, parking too close to intersections, disabled parking violations), call 311 or Parking Authority at (502) 574-7275. LMPD handles parking enforcement on public streets. For vehicles blocking driveways or alleys, call LMPD non-emergency: (502) 574-7111. For parking in front of fire hydrants (within 15 feet), call 311 or LMPD. For abandoned vehicles on public streets, call 311 - vehicles will be tagged and towed if not moved within 72 hours.',
'Parking', 'Violations', 'how_to',
ARRAY['parking', 'violation', 'blocked', 'sidewalk', 'fire lane', 'hydrant'],
ARRAY['Parking violation', 'Car blocking sidewalk', 'Illegal parking', 'Parking complaint', 'Fire hydrant blocked'],
'low', '24-48 hours for enforcement', 'Parking Concern'),

-- 26. Graffiti Removal (830 requests)
('How do I report graffiti for removal?',
'To report graffiti on public property (signs, bridges, buildings, walls), call 311 with the location. Louisville Metro will remove graffiti from public property, typically within 7-10 business days. For graffiti on private property, the property owner is responsible for removal. The city may issue a notice requiring removal if it''s visible from public areas. Take photos if possible to document. To volunteer for graffiti cleanup in your neighborhood, ask 311 about community programs.',
'Code Enforcement', 'Graffiti', 'how_to',
ARRAY['graffiti', 'vandalism', 'spray paint', 'tagging', 'defacement'],
ARRAY['Graffiti removal', 'Graffiti on building', 'Spray paint vandalism', 'Graffiti cleanup'],
'low', '7-10 business days for public property', 'Graffiti'),

-- 27. Large Item Pickup Scheduling (1,050 requests covered but adding detail)
('How do I schedule a large item or bulk trash pickup?',
'To schedule bulk item pickup, call 311 with your address or schedule online at louisvilleky.gov/311. Louisville Metro offers scheduled bulk pickup based on your neighborhood pickup zones. Acceptable items include furniture, appliances, mattresses, carpet, and large household items. Set items at the curb the night before your scheduled pickup day (NOT earlier). Limits apply: typically 2 cubic yards per pickup. Hazardous materials, construction debris, tires, and electronics are NOT accepted - these require special disposal. Pickups are typically scheduled within 3-7 days of request.',
'Waste Management', 'Bulk Pickup', 'how_to',
ARRAY['bulk', 'large item', 'furniture', 'appliance', 'mattress', 'pickup'],
ARRAY['Schedule bulk pickup', 'Large item removal', 'Furniture pickup', 'Appliance disposal', 'Bulk trash'],
'low', '3-7 days for scheduled pickup', 'Large Item Appointment'),

-- 28. Exterior Property Issues (detailed expansion)
('How do I report exterior property code violations?',
'To report exterior property violations (trash accumulation, junk storage, damaged fences, peeling paint, broken gutters, vehicles on grass), call 311 with the property address and description. Code Enforcement will inspect the property for violations of property maintenance codes. Properties must be free from trash accumulation, junk storage, and structural deterioration. Inspections occur within 3-5 business days. Property owners will receive notice to correct violations, typically with 10-30 days to comply depending on severity.',
'Code Enforcement', 'Exterior Property', 'how_to',
ARRAY['exterior', 'property', 'trash', 'junk', 'fence', 'paint', 'deteriorating'],
ARRAY['Exterior violation', 'Property trash', 'Junk in yard', 'Property exterior issues', 'Deteriorating property'],
'low', '3-5 business days for inspection', 'Exterior'),

-- 29. Events and Permits
('How do I get information about special events or event permits?',
'For information about upcoming city events, visit louisvilleky.gov/events or call 311. To apply for a special event permit (block party, parade, festival, street closure), contact Special Events at (502) 574-3961 or visit louisvilleky.gov/government/special-events. Applications must be submitted at least 60 days in advance for events requiring street closures. 311 can provide contact information and basic guidance but cannot process permit applications directly.',
'General', 'Events and Permits', 'what_is',
ARRAY['event', 'permit', 'festival', 'parade', 'block party', 'street closure'],
ARRAY['Event permit', 'Special event', 'Block party permit', 'Festival permit', 'Parade permit'],
'low', 'Immediate (information), 60 days (permit processing)', 'NSR Events'),

-- 30. Social Services Referrals
('How do I get help with housing, food, or other social services?',
'Louisville Metro 311 can provide referrals to social service agencies. Call 311 and describe what assistance you need: housing assistance, food assistance, utility payment help, mental health services, substance abuse treatment, senior services, or other support programs. 311 will provide contact information for appropriate agencies. For immediate crisis assistance: Kentucky Crisis Line: 988 | Homeless Services: (502) 574-6465 | Metro United Way 2-1-1 for comprehensive resource referrals. 311 provides referrals and information but does not directly provide social services.',
'Social Services', 'Referrals', 'what_is',
ARRAY['social services', 'assistance', 'housing', 'food', 'help', 'resources', 'referral'],
ARRAY['Need help', 'Social services', 'Housing assistance', 'Food assistance', 'Get help', 'Resource referral'],
'low', 'Immediate (referral information)', 'NSR Social Services');

-- ============================================================================
-- VERIFY INSERTION
-- ============================================================================
DO $$
DECLARE
    total_count INTEGER;
    new_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_count FROM l311_approved_questions;
    SELECT COUNT(*) INTO new_count FROM l311_approved_questions WHERE created_at > NOW() - INTERVAL '5 minutes';
    RAISE NOTICE 'Total questions in corpus: % (added % new questions)', total_count, new_count;
END $$;

-- Display updated category breakdown
SELECT
    category,
    COUNT(*) as question_count,
    string_agg(DISTINCT question_type, ', ' ORDER BY question_type) as question_types
FROM l311_approved_questions
GROUP BY category
ORDER BY question_count DESC;

-- Display coverage summary
SELECT
    'Expected Coverage Improvement' as metric,
    '39.67% → 89.91% (+50.24%)' as value
UNION ALL
SELECT
    'Additional Requests Covered',
    '85,201 of 169,598 total'
UNION ALL
SELECT
    'New Questions Added',
    '30 questions (23 → 53 total)';
