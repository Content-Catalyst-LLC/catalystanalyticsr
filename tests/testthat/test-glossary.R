test_that("catalyst_glossary documents all core states and derived metrics", {
  glossary <- catalyst_glossary()
  expect_s3_class(glossary, "data.frame")
  expect_true(all(c("name", "label", "kind", "unit", "direction", "notes") %in% names(glossary)))
  expect_true(all(c("K", "H", "N", "C", "P", "A") %in% glossary$name))
  expect_true(all(c("gdp", "emissions", "ans", "carbon_intensity") %in% glossary$name))
  expect_false(anyDuplicated(glossary$name) > 0)
})
