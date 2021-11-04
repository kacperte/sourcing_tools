"""self.driver.find_element_by_xpath("//button[@class='pv-profile-section__card-action-bar "
                                  "pv-skills-section__additional-skills "
                                  "artdeco-container-card-action-bar artdeco-button "
                                  "artdeco-button--tertiary artdeco-button--3 "
                                  "artdeco-button--fluid artdeco-button--muted']").click()"""


#self.driver.execute_script("document.body.style.zoom='50%'")

a = 'Tytuł/stopień wykształcenia\nMagister (Mgr)'

b = 'Kierunek studiów\nGeografia'



pattern1 = r'Tytuł/stopień wykształcenia'
pattern2 = r'Kierunek studiów\n'

if pattern1 in a:
    a = a.replace('\\n','')
    a = a.replace(pattern1, '')
    print(a)
